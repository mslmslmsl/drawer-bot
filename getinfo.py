"""Creates JSON file to use in chatbot"""
import json
import os
import requests
import hashlib
from selenium import webdriver
from openai.embeddings_utils import get_embedding
from bs4 import BeautifulSoup

URL = "https://drawer.nyc/artists/"
EMBEDDING_MODEL = "text-embedding-ada-002"
TESTING = True

text = "This is some text."

# Create an MD5 hash object.
md5_hash = hashlib.md5()

# Update the hash object with the text.
md5_hash.update(text.encode())

# Get the hash value from the hash object.
md5_digest = md5_hash.hexdigest()

# Print the hash value.
# print(md5_digest)


# exit()


def create_file(names, texts, embeddings, filename):
    """Creates a new JSON file with the text and embeddings"""

    json_objects = [{
        "name": names[i],
        "text": j,
        "embedding": embeddings[i],
        "hash": calculate_md5_hash(j)
    } for i, j in enumerate(texts)]

    with open(filename, "w", encoding="utf-8") as outfile:
        json.dump(json_objects, outfile)


def get_info(url: str, driver) -> tuple[str, str, list]:
    """Return artist info from Drawer and related embeddings"""
    driver.get(url)
    driver.implicitly_wait(100)

    page_text = driver.find_element("tag name", "html").text
    start_index = page_text.find("Cart")
    end_index = page_text.find("Get notified when new works")
    abridged_text = page_text[start_index + 5 : end_index - 1]
    lines = abridged_text.split("\n")

    artist_name = lines[0]
    artist_bio = '\n'.join(lines[1:])

    artist_name_and_bio = (
        f"ARTIST NAME: {artist_name}\n"
        f"ARTIST BIO AND WORKS: {artist_bio}"
    )
    embedding = get_embedding(artist_name_and_bio, engine=EMBEDDING_MODEL)

    return artist_name, artist_name_and_bio, embedding


def get_artist_urls(url: str, page_id: str) -> list[str]:
    """Get the URLs for all artist pages"""
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    element = soup.find(id=page_id)

    artist_links = [
        "https://drawer.nyc" + artist_link.get("href")
        for artist_link in element.find_all("a")
        if artist_link.get("href")
    ]

    return artist_links


def calculate_md5_hash(text: str):
    md5_hash = hashlib.md5()
    md5_hash.update(text.encode('utf-8'))
    return md5_hash.hexdigest()


def main():
    """Create a JSON file with all artist info and embeddings for the bot"""
    print("Starting")
    json_texts, json_embeddings, json_names = [], [], []
    filename = "data.json"

    chrome_driver_path = (
        "/Users/michaellyons/Desktop/Code/OAI/myenv/chromedriver"
    )
    webdriver.chrome.driver = chrome_driver_path
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")

    with webdriver.Chrome(options=chrome_options) as driver:
        print("Getting URLs")
        links = get_artist_urls(URL, "artists_list")
        print("Got all URLs")

        iteration_range = links[:2] if TESTING else links

        for link in iteration_range:
            name, bio, embedding = get_info(link, driver)
            print(f"Got info for {name}")
            json_names.append(name)
            json_texts.append(bio)
            json_embeddings.append(embedding)

        print("Creating JSON file")

        create_file(json_names, json_texts, json_embeddings, filename)

    print("All done!")


if __name__ == "__main__":
    main()
