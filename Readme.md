
# CyberDrop Download & Upload Bot

This bot allows users to download files from CyberDrop links and upload them to a specified Telegram chat. It provides the option to rename files after download and before upload.

## Features
- Download files from multiple CyberDrop URLs.
- Upload downloaded media to a Telegram chat or channel.
- Optionally rename downloaded files before uploading.
- Generates video thumbnails and sends them along with video uploads.
- Handles multiple URLs provided in a single command.

## Requirements
- Python 3.11+
- Telegram bot API token
- `credentials.json` file for storing sensitive data (like API keys).

## Installation

### 1. Clone the Repository
```
git clone https://github.com/Bonezajean/Cyberdrop-dl-TG-Bot.git
cd Cyberdrop-dl-TG-Bot
```

### 2. Create `credentials.json`
In the root of the project, create a file called `credentials.json` with your bot’s credentials:

```
{
    "API_ID": "YOUR_API_ID",
    "API_HASH": "YOUR_API_HASH",
    "BOT_TOKEN": "YOUR_BOT_TOKEN",
    "USER_ID": "YOUR_USER_ID",
    "DUMP_ID": "YOUR_DUMP_ID"
}
```

### 3. Install Dependencies
You can install the required dependencies with the following command:

```
pip install -r requirements.txt
```

### 4. Set Permissions (if required)
If you're working in a restricted environment (such as a cloud server like lightning.ai ), you may need to adjust file permissions for certain directories. You can set permissions using:

```
sudo chmod 777 /path/to/directory
```

### 5. Run the Bot
To start the bot, run the main Python script:

```
python main.py
```

## Usage

### Telegram Commands
-`/start`: Start the bot and receive a welcome message.
- `/upload <URL>`: Provide one or more CyberDrop URLs (each on a new line). The bot will download, optionally rename, and upload the files to the specified chat.
- `/help`: Display help information and available commands.

### Example
```
/upload
https://cyberdrop.me/somefolder
https://cyberdrop.me/anotherfolder
```
The bot will download each folder and upload the files to the chat.

### Handling Renaming
After you complete the downloads, the bot will ask if you want to rename the files. Respond with `yes` to provide a new base name for the files or `no` to keep the original names.

### HOW TO USE ON COLAB

for those who uses google colab do  it like this , but you will need to upgrade to Python 3.11 every time you start the runtime ( use method mentonioned here https://stackoverflow.com/a/78413447/20253005 ) :


```
!git clone https://github.com/Bonezajean/Cyberdrop-dl-TG-Bot.git
%cd Cyberdrop-dl-TG-Bot

import json

# Replace these values with your own
API_ID = 123456  # @param {type: "integer"}
API_HASH = "your_api_hash_here"  # @param {type: "string"}
BOT_TOKEN = "your_bot_token_here"  # @param {type: "string"}
USER_ID = 12345678  # @param {type: "integer"}
DUMP_ID = 987654321  # @param {type: "integer"}

# Create the credentials dictionary
credentials = {
    "API_ID": str(API_ID),
    "API_HASH": API_HASH,
    "BOT_TOKEN": BOT_TOKEN,
    "USER_ID": str(USER_ID),
    "DUMP_ID": str(DUMP_ID)
}

# Save to a credentials.json file
with open("credentials.json", "w") as json_file:
    json.dump(credentials, json_file, indent=4)

!pip install -r requirements.txt
!python main.py

```
