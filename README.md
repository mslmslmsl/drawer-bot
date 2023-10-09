# Chatbot for Art Advice

This chatbot provides a conversational interface for learning about [Drawer](https://drawer.nyc/) artists and includes two main components:

1. **getinfo.py**: Use this script to fetch artist info (name, bio, works) from the Drawer [Artists page](https://drawer.nyc/artists/) and store the data in `data.json`. Before using this script, make sure to install the required dependencies (incl., `webdriver`) and update the webdriver path.

2. **chat.py**: Use this script to interact with the art-advisor bot. The bot is powered by OpenAI's [Chat API](https://platform.openai.com/docs/api-reference/chat). The advisor's responses include context from `data.json`, which includes information about artists most related to the user's prompt. By default, the bot includes the bios for the three most relevant artists, but you can adjust this number by using the `--context n` argument to specify the number of artist bios you want to include.

Note: to run either script, you need to set your OpenAI API key as the `OPENAI_API_KEY` environment variable with the command `export OPENAI_API_KEY=<YOUR_API_KEY>` or update the scripts to include your API key.

Note: To execute either script, you must configure your OpenAI API key as the `OPENAI_API_KEY`` environment variable using the command `export OPENAI_API_KEY=<YOUR_API_KEY>`. Alternatively, you can modify the scripts to include your API key directly.