import requests
r = requests.get("https://example.com")

for cookie in r.cookies:
    print(cookie.name, cookie.secure, cookie.has_nonstandard_attr('HttpOnly'))