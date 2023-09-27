This chatbot has two files:

1. Use `getinfo.py` to pull artist info (name, bio, works) from the Drawer [Artists page](https://drawer.nyc/artists/). The data is save to `data.json`. (To use this, you will need to install `webdriver` and update the webdriver path.)
2. Use `chat.py` to chat with an art advisor. The advisor's responses use OpenAI's Chat API and includes information about the three artists most related to the user prompt as context (from `data.json`).