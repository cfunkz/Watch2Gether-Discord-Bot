import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

W2G_API_KEY = os.getenv("W2G_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = os.getenv("DB_FILE", "user_rooms.db")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
ROLE_ID = int(os.getenv("ROLE_ID", "0"))
MAX_LOG_SIZE = int(os.getenv("MAX_LOG_SIZE", "33554432"))
ROTATE_LOGS = int(os.getenv("ROTATE_LOGS", "5"))
LOG_FILE = os.getenv("LOG_FILE", "discord.log")
DEFAULT_AVATAR = os.getenv("DEFAULT_AVATAR", "https://i.ibb.co/TMnHDzL2/watchparty.png")
MAX_USER_ROOM = int(os.getenv("MAX_USER_ROOM", "10"))
