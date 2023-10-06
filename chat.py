"""Chatbot that uses Drawer artists page as context"""
import json
import random
import argparse
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
DEFAULT_CONTEXT = 3  # default number of artist profiles to add to each prompt
INSTRUCTIONS = """
    Answer my QUERY with the history above in mind.
    If relevant, also base your response on the CONTEXT below.
    The text 'The work above is sold' means that the lines above identify an
    artwork that has sold.
    Keep your responses very brief.
    Do not just paste in text in the format provided to you.
    Don't say things like 'based on the info provided.'
    Make sure your responses are complete sentences in conversational English.
    """
PERSONALITY = random.choice([
    "You are an arrogant, elitist art advisor",
    "You are a friendly, helpful art advisor",
    "You are a cynical, bored art advisor"
])
MAX_LENGTH = 4097
ENCODING = tiktoken.encoding_for_model(GPT_MODEL)

# Let users specify the number of profiles to include as context (default=3)
parser = argparse.ArgumentParser()
parser.add_argument(
    "--context",
    type=int,
    default=DEFAULT_CONTEXT,
    help=(
        "Specify number of artist profiles to include in "
        "prompts (default: %(default)s)"
    )
)
args = parser.parse_args()

if args.context and (0 <= int(args.context) <= 20):
    context_to_include = int(args.context)
else:
    raise ValueError("The context must be an integer between 0 and 20.")


def measure_and_truncate_prompt(prompt):
    """Calculate token length and remove second object (keep `system`)"""
    while count_tokens(prompt) > MAX_LENGTH:
        del prompt[1]  # delete the oldest message other than the system one
    return prompt


def get_data(filename):
    """Loads the JSON that includes artist info and embeddings"""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def count_tokens(messages, model=GPT_MODEL):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows
        # <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        return count_tokens(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        return count_tokens(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"count_tokens() is not implemented for model {model}."
        )

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


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
        distances = distances_from_embeddings(
            prompt_embedding,
            data_embeddings
        )
        indices_of_nearest_neighbors = (
            indices_of_nearest_neighbors_from_distances(distances)
        )

        # create full prompt with instructions, prompt, and context
        full_prompt = f"{INSTRUCTIONS} \n\nCONTEXT:"
        for i, neighbor_index in enumerate(indices_of_nearest_neighbors):
            if neighbor_index < context_to_include:
                full_prompt += data[i]["text"]
        full_prompt += f"\n\nQUERY: {prompt}"

        # add full prompt to list
        messages.append({"role": "user", "content": full_prompt})
        messages = measure_and_truncate_prompt(messages)

        # get OAI response
        response = openai.ChatCompletion.create(
            model=GPT_MODEL, messages=messages, max_tokens=256
        )

        # print the response
        print(response["choices"][0]["message"]["content"])

        # remove context and instructions from the list to save on tokens
        messages.pop()
        messages.append({"role": "user", "content": prompt})

        # add the response to our history
        messages.append(
            {
                "role": "assistant",
                "content": response["choices"][0]["message"]["content"],
            }
        )


if __name__ == "__main__":
    main()
