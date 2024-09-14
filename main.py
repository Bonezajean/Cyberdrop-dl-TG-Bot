
import yaml
import os
import time
import asyncio
import logging
from subprocess import run
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from moviepy.editor import VideoFileClip
import nest_asyncio
import json

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Setting up logging
logging.basicConfig(level=logging.INFO)

# Load credentials from the JSON file
with open('credentials.json', 'r') as f:
    credentials = json.load(f)

# Assign credentials to variables
API_ID = credentials['API_ID']
API_HASH = credentials['API_HASH']
BOT_TOKEN = credentials['BOT_TOKEN']
USER_ID = credentials['USER_ID']
DUMP_ID = credentials['DUMP_ID']

# Initialize the Pyrogram client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Define download directory
download_path = "/teamspace/studios/this_studio/Downloads/Cyberdrop-DL Downloads/"

# Store states for users
user_states = {}

# Function to download files from CyberDrop
def download_from_cyberdrop(download_url: str):
    download_command = f"cyberdrop-dl --no-ui --download -- {download_url}"
    result = run(download_command, shell=True)
    if result.returncode != 0:
        raise Exception(f"Download failed for URL: {download_url}")

# Progress bar for uploads
async def progress_bar(current, total):
    print(f"Uploading {current}/{total} bytes")

# Function to generate a video thumbnail and get the video duration
def generate_thumbnail_and_get_duration(video_path, thumbnail_directory):
    # Ensure the thumbnail directory exists
    os.makedirs(thumbnail_directory, exist_ok=True)

    # Get the video filename without extension
    video_filename = os.path.splitext(os.path.basename(video_path))[0]

    # Define the thumbnail path
    thumbnail_path = os.path.join(thumbnail_directory, f"{video_filename}_thumbnail.jpg")

    # Generate thumbnail and get duration
    with VideoFileClip(video_path) as clip:
        duration = int(clip.duration)  # Get video duration in seconds
        clip.save_frame(thumbnail_path, t=1.0)  # Save a frame at the 1-second mark for thumbnail

    return thumbnail_path, duration

# Upload function to Telegram
async def upload_file(bot, chat_id, file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    file_type = "video" if file_name.endswith(('mp4', 'mkv', 'webm', 'mov')) else "document"

    try:
        if file_type == "video":
            # Define the directory to save thumbnails
            thumbnail_directory = "/teamspace/studios/this_studio/thumbnails/"

            # Generate thumbnail and get video duration
            thumbnail_path, video_duration = generate_thumbnail_and_get_duration(file_path, thumbnail_directory)

            # Send video with duration and thumbnail
            await bot.send_video(
                chat_id=DUMP_ID,
                video=file_path,
                caption=f"{file_name}",
                thumb=thumbnail_path,
                supports_streaming=True,
                duration=video_duration,
                progress=progress_bar
            )

            # Optionally, remove the thumbnail after sending the video
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

        elif file_name.lower().endswith(('jpg', 'jpeg', 'png', 'gif')):
            # Upload as a photo
            await bot.send_photo(
                chat_id=DUMP_ID,
                photo=file_path,
                caption=f"{file_name}",
                progress=progress_bar
            )
        else:
            # Upload as a document
            await bot.send_document(
                chat_id=DUMP_ID,
                document=file_path,
                caption=f"{file_name}",
                progress=progress_bar
            )

        # Remove the file after successful upload
        os.remove(file_path)

    except FloodWait as e:
        await asyncio.sleep(e.x)
    except Exception as e:
        logging.error(f"Error uploading {file_path}: {e}")

# Function to wait for the creation of the settings.yaml file
def wait_for_yaml_file():
    file_path = '/teamspace/studios/this_studio/AppData/Configs/Default/settings.yaml'
    timeout = 60  # Max wait time in seconds
    start_time = time.time()

    while not os.path.exists(file_path):
        if time.time() - start_time > timeout:
            raise FileNotFoundError(f"File not found: {file_path}")
        time.sleep(1)

    # Load and update the YAML file
    with open(file_path, 'r') as file:
        settings = yaml.safe_load(file)

    # Update the 'ignore_history' option to 'true'
    settings['Runtime_Options']['ignore_history'] = True

    # Save the updated settings back to the YAML file
    with open(file_path, 'w') as file:
        yaml.dump(settings, file, default_flow_style=False)

    print("Updated 'ignore_history' to 'true' in settings.yaml.")

# /start command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Hello! Send me a CyberDrop URL with the /upload command to start downloading and uploading the media!")

# /upload command handler
@app.on_message(filters.command("upload"))
async def upload(client, message):
    try:
        # Extract multiple URLs from the message, assuming each URL is on a new line
        urls = message.text.split('\n')[1:]  # Split by newline and ignore the command part
    except IndexError:
        await message.reply_text("Please provide one or more CyberDrop URLs after the /upload command, each on a new line!")
        return

    chat_id = message.chat.id
    await message.reply_text(f"📥 Starting to download from {len(urls)} links...")

    # Download each URL one by one
    for idx, url in enumerate(urls, start=1):
        try:
            await message.reply_text(f"Downloading {idx}/{len(urls)}: {url}")
            download_from_cyberdrop(url)  # Download the file
            await message.reply_text(f"Download {idx}/{len(urls)} complete.")
        except Exception as e:
            await message.reply_text(f"❌ Failed to download from URL: {url}\nError: {e}")
            continue  # Move to the next URL even if this one fails

    # After all downloads are complete
    await message.reply_text("✅ All downloads completed. Checking settings...")

    # Wait for the settings.yaml file and update it when created
    try:
        wait_for_yaml_file()
    except FileNotFoundError as e:
        await message.reply_text(f"❌ {e}")
        return

    # Ask if the user wants to rename the files
    await message.reply_text("Do you want to rename the files? (yes/no)")

    # Store the user's state for renaming decision
    user_states[chat_id] = {"state": "awaiting_rename_decision"}

# Handling user responses to renaming decision
@app.on_message(filters.text)
async def handle_user_response(client, message):
    chat_id = message.chat.id

    # Check if the user has an active state
    if chat_id not in user_states:
        return

    user_state = user_states[chat_id]

    # Handle rename decision
    if user_state.get("state") == "awaiting_rename_decision":
        if message.text.lower() == "yes":
            await message.reply_text("Please provide the new name:")
            user_state["state"] = "awaiting_new_name"
        else:
            user_state["rename"] = False
            await upload_files(client, chat_id)

    # Handle new name input
    elif user_state.get("state") == "awaiting_new_name":
        user_state["rename"] = True
        user_state["new_name"] = message.text
        await upload_files(client, chat_id)

# Function to upload files to Telegram (unchanged)
async def upload_files(client, chat_id):
    rename = user_states[chat_id].get("rename", False)
    new_name = user_states[chat_id].get("new_name", None)

    # Upload files to Telegram
    for idx, (root, dirs, files) in enumerate(os.walk(download_path)):
        for i, file in enumerate(files):
            file_path = os.path.join(root, file)

            if rename and new_name:
                # Generate new file name with numbering if multiple files
                file_extension = os.path.splitext(file)[1]
                renamed_file = f"{new_name}_{i + 1}{file_extension}"
                new_file_path = os.path.join(root, renamed_file)
                os.rename(file_path, new_file_path)
                file_path = new_file_path

            await upload_file(client, chat_id, file_path)

    await client.send_message(chat_id, "✅ All files uploaded successfully!")
    del user_states[chat_id]  # Clear user state after uploading files


# /help command handler
@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text("/upload <URL> - To upload media from the given CyberDrop URL\n/cancel - To cancel the current operation")

# Run the bot in the event loop
async def run_bot():
    await app.start()
    logging.info("Bot started.")
    try:
        await asyncio.Event().wait()  # Keeps the bot running
    finally:
        await app.stop()
        logging.info("Bot stopped.")

# Start the bot
asyncio.run(run_bot())
