# Chatbot for Art Advice

This chatbot provides a conversational interface for learning about [Drawer](https://drawer.nyc/) artists and includes two main components:

1. **getinfo.py**: Use this script to fetch artist info (name, bio, works) from the Drawer [Artists page](https://drawer.nyc/artists/) and store the data in `data.json`. Before using this script, make sure to install the required dependencies (incl., `webdriver`) and update the webdriver path.

2. **chat.py**: Use this script to interact with the art-advisor bot. The bot is powered by OpenAI's Chat API. The advisor's responses include context from `data.json`, which includes information about the three artists most related to the user's prompt.
