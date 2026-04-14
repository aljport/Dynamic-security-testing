import requests
import time

def checkCookies(url):
    r = requests.get(url)
    for cookie in r.cookies:
        security = cookie.secure
        httpOnly = cookie.has_nonstandard_attr('HttpOnly')
        if not security:
            print("Vulnerability: " + cookie.name + "")
        if not httpOnly:
            print("Vulnerability: " + cookie.name + " does not have the HttpOnly attribute")
        if (security and httpOnly):
            print("Cookies are secure and have HttpOnly flags")

# code403 = "unauthorized"
# If timeout occurs another code will be returned
# Link must be a login URL
# Sample URL = "https://vsco.co/user/login"

def checkRateLimit(url):
    session = requests.Session()

    # Login attempt
    payload = {
        "username": "test",
        "password": "wrongpassword"
    }

    for i in range(11):
        login_response = session.post(url, data=payload)
        if login_response.status_code != 403 and i < 11:
            print("Successful login timeout (within 10 attempts).")
            break
        time.sleep(4)
    else:
        print("Vulnerability: No login timeout within 10 attempts.")

