import time
import requests
import hashlib

session = requests.Session()

code403 = "unauthorized"
url = "https://vsco.co/user/login"

def hash_html(text):
    return hashlib.sha256(text.encode()).hexdigest()

# Login attempt
payload = {
    "username": "test",
    "password": "wrongpassword"
}

for i in range(11):
    login_response = session.post(url, data=payload)
    if (login_response.status_code != 403):
        print("Login timeouts should occur after 10 attempts.")
    time.sleep(4)
