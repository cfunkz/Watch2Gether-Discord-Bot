import aiosqlite
from discord.ext import commands, tasks
from config import DB_FILE  # make sure this points to your database file
from utils.logger import logger

class CleanUpCog(commands.Cog):
    """Cog that cleans up deleted rooms from the database daily."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.clean_deleted_rooms.start()

    def cog_unload(self):
        self.clean_deleted_rooms.cancel()

    @tasks.loop(hours=24)
    async def clean_deleted_rooms(self):
        """Delete rooms where is_deleted == True."""
        await self.bot.wait_until_ready()

        logger.info("Starting cleanup of deleted rooms...")

        try:
            async with aiosqlite.connect(DB_FILE) as db:
                await db.execute("DELETE FROM rooms WHERE is_deleted = 1")
                await db.commit()

            logger.info("Deleted all rooms marked as deleted.")
        except Exception as e:
            logger.exception("Error during room cleanup: %s", e)

    @clean_deleted_rooms.before_loop
    async def before_clean(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(CleanUpCog(bot))
