
# Duck duck go browser

from ddgs import DDGS

query = 'site:archive.apache.org "Index of"'

with DDGS() as ddgs:
    results = ddgs.text(query, max_results=10)

    for r in results:
        print(r["title"])
        print(r["href"])
        print()