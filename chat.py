"""Chatbot that uses Drawer artists page as context"""
import json
import openai
from openai.embeddings_utils import (
    get_embedding,
    distances_from_embeddings,
    indices_of_nearest_neighbors_from_distances,
)

EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"
CONTEXT_TO_INCLUE = 3

def get_data(filename):
    """Loads the JSON that includes artist info and embeddings"""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


data = get_data("data.json")

data_embeddings = []
for entry in data:
    data_embeddings.append(entry["embeddings"])

messages = []
messages.append({"role": "system", "content": "You are an art advisor."})
print("Hi I'm an art advisor how can I help you?")

while True:
    prompt = input("> ")
    full_prompt = (
        "Answer my QUERY with the CONTEXT below, but keep it VERY brief. "
        "Also, do not just paste in text in the format provided to you. And "
        "make sure your responses are complete sentences in conversatinoal "
        f"English - DO NOT just paste facts. QUERY: {prompt}\n\nCONTEXT:"
    )

    prompt_embedding = get_embedding(prompt, engine=EMBEDDING_MODEL)
    distances = distances_from_embeddings(prompt_embedding, data_embeddings)
    indices_of_nearest_neighbors = indices_of_nearest_neighbors_from_distances(
        distances
    )

    for i in indices_of_nearest_neighbors:
        if indices_of_nearest_neighbors[i] < CONTEXT_TO_INCLUE:
            full_prompt += data[i]["text"]

    messages.append({"role": "user", "content": full_prompt})
    response = openai.ChatCompletion.create(
        model=GPT_MODEL, messages=messages, max_tokens=256
    )

    messages.append(
        {
            "role": "assistant",
            "content": response["choices"][0]["message"]["content"]
        }
    )

    print(response["choices"][0]["message"]["content"])
