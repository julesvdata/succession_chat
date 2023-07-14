import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

start_url = "https://succession.fandom.com/wiki/Succession_Wiki"
base_url = "https://succession.fandom.com"
visited = set()
results = {}


def get_text_from_page(url):
    """Extracts all text from a given url

    Args:
        url (str): The URL of the Wikipedia page

    Returns:
        str: The extracted text from the page
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    # Extract all text from the HTML
    text = " ".join(t.strip() for t in soup.stripped_strings)

    return text


def crawl(url, depth=0):
    """Crawls a given URL and extracts all text from the page

    Args:
        url (str): The URL of the Wikipedia page
        depth (int): The current depth of the crawl
    """

    print(url)
    if depth > 2:
        return

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    visited.add(url)

    # Extract and print all text from the current page
    text = get_text_from_page(url)
    results[url] = text  # Store the text in the results dictionary

    # Find all links on the current page
    for link in soup.find_all("a", href=True):
        new_url = urljoin(base_url, link["href"])
        if new_url not in visited and new_url.startswith(base_url + "/wiki/"):
            crawl(new_url, depth + 1)


crawl(start_url)

df = pd.DataFrame(list(results.items()), columns=["url", "text"])
df.to_csv("data/succession_wiki_text.csv", index=False)
