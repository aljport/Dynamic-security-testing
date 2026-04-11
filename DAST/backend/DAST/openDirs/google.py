import requests
import os
API_KEY = "AIzaSyCevFaMd0fQPtscn7JvmH570GGSJkW7eX4"
SEARCH_ENGINE_ID = "c6f76787fd1124efd"
query = 'site:archive.apache.org "Index of"'
url = "https://www.googleapis.com/customsearch/v1"

params = {
    "key": API_KEY,
    "cx": SEARCH_ENGINE_ID,
    "q": query,
    "num": 10
}

response = requests.get(url, params=params)
data = response.json()

# Print results (similar to your DDG code)
for item in data.get("items", []):
    print(item["title"])
    print(item["link"])
    print()