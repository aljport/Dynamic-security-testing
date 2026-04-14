
# Duck duck go browser

from ddgs import DDGS


def checkOpenDirs(url):
    query = f'site:{url} "Index of"'

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=10)
        links = []
        for r in results:
            links.append(r["href"])
        return {
            "vulnerable": True,
            "links": links
        }