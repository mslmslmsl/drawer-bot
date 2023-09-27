"""Chatbot that uses Drawer artists page as context"""
import json
import random
import openai
import tiktoken
from openai.embeddings_utils import (
    get_embedding,
    distances_from_embeddings,
    indices_of_nearest_neighbors_from_distances,
)

# constants
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"
CONTEXT_TO_INCLUE = 3
INSTRUCTIONS = (
    "Answer my QUERY with the history above in mind and, if relevant, the "
    "CONTEXT below. Note that if you see the text 'The work above is sold,' "
    "that means that the lines above identify an artwork that has sold. Also "
    "keep these rules in mind: (1) keep your responses very brief; (2) do not "
    "just paste in text in the format provided to you and don't say things "
    "like 'based on the info provided'; and (3) make sure your responses are "
    "complete sentences in conversational English."
)
PERSONALITY = random.choice([
    "You are an arrogant, elitist art advisor",
    "You are a friendly, helpful art advisor",
    "You are a cynical, bored art advisor"
])
MAX_LENGTH = 4096
ENCODING = tiktoken.encoding_for_model(GPT_MODEL)


def count_tokens(prompt):
    """Return token count for entire JSON"""
    token_count = len(prompt) * 13 + 2  # for { } ' , : [ ]
    for entry in prompt:
        for key, value in entry.items():
            token_count += len(ENCODING.encode(key))
            token_count += len(ENCODING.encode(value))
    return token_count


def measure_and_truncate_prompt(prompt):
    """Calculate token length and remove second object (keep `system`)"""
    while count_tokens(prompt) >= MAX_LENGTH:
        del prompt[1]  # delete the oldest message other than the system one
    return prompt


def get_data(filename):
    """Loads the JSON that includes artist info and embeddings"""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    """Run the bot"""

    # load the bios of all the artists on the Drawer page
    data = get_data("data.json")

    # get the embeddings for all artists' bios
    data_embeddings = []
    for entry in data:
        data_embeddings.append(entry["embedding"])

    # create the list of messages that will be used
    messages = []
    messages.append({"role": "system", "content": PERSONALITY})
    print("I'm an art advisor; how can I help you?")

    # loop for chatting
    while True:
        # get user input
        prompt = input("> ")
        if prompt.lower() == "exit":
            # add exit condition to while True loop
            print("Bye bye")
            break

        # get prompt embedding and context negihbors
        prompt_embedding = get_embedding(prompt, engine=EMBEDDING_MODEL)
        distances = distances_from_embeddings(prompt_embedding, data_embeddings)
        indices_of_nearest_neighbors = (
            indices_of_nearest_neighbors_from_distances(distances)
        )

        # create full prompt with instructions, prompt, and context
        full_prompt = f"{INSTRUCTIONS} \n\nCONTEXT:"
        for i in indices_of_nearest_neighbors:
            if indices_of_nearest_neighbors[i] < CONTEXT_TO_INCLUE:
                full_prompt += data[i]["text"]
        full_prompt += f"\n\nQUERY: {prompt}"

        # add full prompt to list
        messages.append({"role": "user", "content": full_prompt})
        messages = measure_and_truncate_prompt(messages)

        # get OAI response
        response = openai.ChatCompletion.create(
            model=GPT_MODEL, messages=messages, max_tokens=256
        )

        # remove context and instructions from the list to save on tokens
        messages.pop()
        messages.append({"role": "user", "content": prompt})
        messages.append(
            {
                "role": "assistant",
                "content": response["choices"][0]["message"]["content"],
            }
        )

        # print the response
        print(response["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()
