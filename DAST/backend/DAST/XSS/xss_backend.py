#XSS BACKEND
#TO CALL USE:   scan_xss(website)



import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import html


PAYLOAD = "<xss_test_marker>"

HEADERS = {
    "User-Agent": "DAST-Scanner-Senior-Project"
}

def get_forms(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.find_all("form"), r.text


def get_form_details(form):
    action = form.attrs.get("action") or ""
    method = form.attrs.get("method", "get").lower()
    inputs = []
    for tag in form.find_all(["input", "textarea"]):
        name = tag.attrs.get("name")
        type_ = tag.attrs.get("type", "text")
        if name:
            inputs.append({"name": name, "type": type_})
    return {"action": action, "method": method, "inputs": inputs}


def submit_form(form_details, url, payload):
    target = urljoin(url, form_details["action"])
    data = {i["name"]: payload for i in form_details["inputs"]}
    if form_details["method"] == "post":
        return requests.post(target, data=data, headers=HEADERS)
    else:
        return requests.get(target, params=data, headers=HEADERS)


def is_exploitable_reflection(response_text, payload):
    if payload in response_text:
        return "raw_reflection", "Payload reflected unencoded directly"
    if re.search(rf"<script[^>]*>.*?{re.escape(payload)}.*?</script>", response_text, re.IGNORECASE | re.DOTALL):
        return "script_injection", "Payload found inside <script>"
    if re.search(rf'on\w+\s*=\s*["\']?[^"\']*{re.escape(payload)}', response_text, re.IGNORECASE):
        return "event_handler", "Payload found in event handler"
    if re.search(rf'<[a-zA-Z][^>]*\s[^>]*{re.escape(payload)}[^>]*>', response_text, re.IGNORECASE | re.DOTALL):
        return "attribute_injection", "Payload found inside an HTML tag"
    return None, None


def detect_dom_xss(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    sinks = ["innerHTML", "document.write", "outerHTML", "eval(", "insertAdjacentHTML"]
    sources = ["location.search", "location.hash", "document.URL", "document.location", "document.referrer"]
    for script in soup.find_all("script"):
        code = script.text
        for source in sources:
            for sink in sinks:
                if source in code and sink in code:
                    return f"{source} -> {sink}"
    return None


def scan_xss(url):
    try:
        forms, page_source = get_forms(url)
    except Exception as e:
        print(f"XSS Vulnerability : NO")
        print(f"Error      : {e}")
        return

    vector, description, method = None, None, None

    # Check DOM XSS first
    dom_issue = detect_dom_xss(page_source)
    if dom_issue:
        vector = "dom_xss"
        description = f"Unsafe data flow detected: {dom_issue}"
        method = "DOM"

    # Check reflected XSS
    if not vector:
        for form in forms:
            details = get_form_details(form)
            if not details["inputs"]:
                continue
            try:
                response = submit_form(details, url, PAYLOAD)
                v, d = is_exploitable_reflection(response.text, PAYLOAD)
                if v:
                    vector = v
                    description = d
                    method = details["method"].upper()
                    break
            except Exception:
                continue

    print()
    if vector:
        print(f"XSS Vulnerability : YES")
        print(f"Type       : {vector}")
        print(f"Method     : {method}")
        print(f"Detail     : {description}")
    else:
        print(f"XSS Vulnerability : NO")
        print(f"Detail     : No XSS patterns detected")
    print()
