from discord import Intents
from discord.ext import commands
from utils.database import init_db
from utils.logger import logger
from config import BOT_TOKEN

# === Bot Intent Setup ===
intents = Intents.default()
intents.message_content = True
intents.guilds = True

# === Bot Initialization ===
bot = commands.Bot(command_prefix="!", intents=intents)

# === On Bot Ready tasks ===
@bot.event
async def on_ready():
    if bot.user is not None:
        logger.info(f"Logged in as {bot.user} ({bot.user.id})")
    else:
        logger.warning("Bot user is None. Could not log user info.")
        exit(1)
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        logger.exception(f"Failed to sync commands: {e}")

# === Setup Hook runs once for Database and Extensions ===
@bot.event
async def setup_hook():
    logger.info("Setting up the bot...")
    # Initialize the database
    await init_db()
    logger.info("Database initialized.")
    await load_extensions()
    logger.info("Extensions loaded.")

async def load_extensions():
    await bot.load_extension("cogs.watch")
    await bot.load_extension("cogs.admin")
    await bot.load_extension("cogs.cleaner")

# === Main entry ===
if __name__ == "__main__":
    bot.run(BOT_TOKEN, log_handler=None)