"""Creates JSON file to use in chatbot"""
import json
import os
import requests
from selenium import webdriver
from openai.embeddings_utils import get_embedding
from bs4 import BeautifulSoup

URL = "https://drawer.nyc/artists/"
EMBEDDING_MODEL = "text-embedding-ada-002"
TESTING = True


def create_file(names, texts, embeddings, filename):
    """Creates the JSON file with the embeddings"""
    if os.path.exists(filename):
        os.remove(filename)

    json_objects = []

    for i, j in enumerate(texts):
        print(f"Adding {names[i]} to file")
        json_objects.append({"text": j, "embeddings": embeddings[i]})

    with open(filename, "w", encoding="utf-8") as outfile:
        json.dump(json_objects, outfile)


def get_info(url: str, driver) -> tuple[str, str, list]:
    """Return artist info from Drawer and related embeddings"""
    driver.get(url)
    driver.implicitly_wait(100)

    page_text = driver.find_element("tag name", "html").text
    start_index = page_text.find("Cart")
    end_index = page_text.find("Get notified when new works")
    modified_text = page_text[start_index + 5 : end_index - 1]

    artist_name = modified_text.split("\n")[0]
    rest_of_text = modified_text.split("\n")[1:]
    final_name = f"ARTIST NAME: {artist_name}"
    final_bio = "ARTIST BIO AND WORKS: " + "\n".join(rest_of_text)
    final_text = f"{final_name}\n{final_bio}"

    embedding = get_embedding(final_text, engine=EMBEDDING_MODEL)

    return artist_name, final_text, embedding


def get_artist_urls(url: str, page_id: str) -> list[str]:
    """Get the URLs for all artist pages"""
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    element = soup.find(id=page_id)
    artist_links = []
    for artist_link in element.find_all("a"):
        href = artist_link.get("href")
        if href:
            artist_links.append("https://drawer.nyc" + href)

    return artist_links


def main():
    """Create a JSON file with all artist info and embeddings for the bot"""
    print("Starting")
    json_texts = []
    json_embeddings = []
    json_names = []
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

        for link in links[:2] if TESTING else links:
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
