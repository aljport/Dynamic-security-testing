import requests
import time

def checkCookies(url):
    r = requests.get(url)
    results = []
    for cookie in r.cookies:
        security = cookie.secure
        httpOnly = cookie.has_nonstandard_attr('HttpOnly')
        if (not security) and (not httpOnly):
            results.append("Vulnerabilities: " + cookie.name + "does not have secure flag or HttpOnly attribute")
        else: 
            if not security:
                results.append("Vulnerability: " + cookie.name + "does not have secure flag")
            if not httpOnly:
                results.append("Vulnerability: " + cookie.name + " does not have the HttpOnly attribute")
    
    return results

# code403 = "unauthorized"
# If timeout occurs another code will be returned
# Link must be a login URL
# Sample URL = "https://vsco.co/user/login"

def checkRateLimit(url):
    session = requests.Session()

    results = []
    # Login attempt
    payload = {
        "username": "test",
        "password": "wrongpassword"
    }

    for i in range(11):
        login_response = session.post(url, data=payload)
        if login_response.status_code != 403 and i < 11:
            print(login_response.status_code)
            return []
    else:
        results.append("No login timeout within 10 attempts.")

    return results


def checkAuth(url):
    vulnerable = False
    count = 0
    resultsCookies = checkCookies(url)
    resultsLimit = checkRateLimit(url)

    for i in range(len(resultsCookies)):
        if resultsCookies[i][0] == "V":
            vulnerable = True
    if vulnerable:
        count += 1
    
    if resultsLimit:
        vulnerable = True
        count += 1

    return  {
        "vulnerable": vulnerable,
        "cookies": resultsCookies,
        "limits": resultsLimit,
        "findings_count": count
    }

