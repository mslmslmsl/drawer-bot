"""Creates JSON file to use in chatbot"""
import json
import os
import requests
from selenium import webdriver
from openai.embeddings_utils import get_embedding
from bs4 import BeautifulSoup

URL = "https://drawer.nyc/artists/"
EMBEDDING_MODEL = 'text-embedding-ada-002'


def create_file(names, texts, embeddings, filename):
    """Creates the JSON file with the embeddings"""
    if os.path.exists(filename):
        os.remove(filename)  # Delete the file if it exists
    
    json_objects = []
    
    for i, j in enumerate(texts):
        print(f"Adding {names[i]} to file")
        json_entry = {
            "text": j,
            "embeddings": embeddings[i]
        }
        json_objects.append(json_entry)

    with open(filename, "w", encoding="utf-8") as outfile:
        json.dump(json_objects, outfile)
        # outfile.write("\n")


def get_info(url: str) -> tuple[str, str, list]:
    """Retrun artist info from Drawer and related embeddings"""
    driver.get(url)
    driver.implicitly_wait(100)

    page_text = driver.find_element("tag name", "html").text
    start_index = page_text.find("Cart")
    end_index = page_text.find("Get notified when new works")
    modified_text = page_text[start_index+5:end_index-1]

    artist_name = modified_text.split('\n')[0]
    rest_of_text = modified_text.split('\n')[1:]
    final_name = f"ARTIST NAME: {artist_name}"
    final_bio = "ARTIST BIO AND WORKS: " + '\n'.join(rest_of_text)
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
            artist_links.append('https://drawer.nyc'+href)

    return artist_links


print("Starting")
json_texts = []
json_embeddings = []
json_names = []
FILENAME = "data.json"

CHROME_DRIVER_PATH = '/Users/michaellyons/Desktop/Code/OAI/myenv/chromedriver'
webdriver.chrome.driver = CHROME_DRIVER_PATH
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')

# Create the WebDriver with the specified options.
with webdriver.Chrome(options=chrome_options) as driver:

    print("Getting URLs")
    links = get_artist_urls(URL, "artists_list")
    print("Got all URLs")

    for link in links[:2]:
        x, y, z = get_info(link)
        print(f"Got info for {x}")
        json_names.append(x)
        json_texts.append(y)
        json_embeddings.append(z)

    print("Creating JSON file")
    create_file(json_names, json_texts, json_embeddings, FILENAME)

print("All done!")