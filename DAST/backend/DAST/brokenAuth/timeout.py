import requests
import hashlib

session = requests.Session()

login_url = "https://juice-shop.herokuapp.com/#/login"
protected_url = "https://juice-shop.herokuapp.com/#/login"

# ----------------------------
# Helper: hash HTML for comparison
# ----------------------------
def hash_html(text):
    return hashlib.sha256(text.encode()).hexdigest()

# ----------------------------
# 1. Get baseline (before login)
# ----------------------------
baseline = session.get(protected_url)
baseline_hash = hash_html(baseline.text)

print("[*] Baseline status:", baseline.status_code)

# ----------------------------
# 2. Attempt login
# ----------------------------
payload = {
    "username": "test",
    "password": "wrongpassword"
}

login_response = session.post(login_url, data=payload)

print("[*] Login status:", login_response.status_code)

# ----------------------------
# 3. Try protected page AFTER login
# ----------------------------
after = session.get(protected_url)
after_hash = hash_html(after.text)

# ----------------------------
# 4. CHECK 1: Session-based auth success
# ----------------------------
session_worked = (
    "login" not in after.url.lower()
    and after.status_code == 200
    and "password" not in after.text.lower()
)

# ----------------------------
# 5. CHECK 2: HTML difference detection
# ----------------------------
html_changed = baseline_hash != after_hash

# ----------------------------
# 6. RESULT LOGIC
# ----------------------------
print("\n=== AUTH TEST RESULT ===")

if session_worked:
    print("✅ Session indicates authentication may be working")
else:
    print("❌ Session did NOT indicate successful authentication")

if html_changed:
    print("ℹ️ HTML changed between states")
else:
    print("⚠️ HTML did NOT change (possible weak auth or static page)")

if not session_worked and not html_changed:
    print("🚨 Possible broken authentication (no session + no state change)")