import requests

url = "https://example.com/login"

data = {
    "username": "test",
    "password": "wrong"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.post(url, data=data, headers=headers)

print(response.text)