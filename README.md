# Python script for monitoring for stuff on sites and sending notifications to telegram

## Installation
```
pip install -r requriements.txt
````

---
## Usage:
1. Put your bot token into `BOT_TOKEN` env variable
2. Edit config to your needs. Don't forget to add your chat_id and proper selectors
3. Run `python __main__.py config.yaml`

---
## How to get your `chat_id`
1. Send a message to your bot
2. Go to `https://api.telegram.org/bot<your_bot_token>/getUpdates`
3. Copy chat_id from there
