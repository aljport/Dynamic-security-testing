import requests


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
