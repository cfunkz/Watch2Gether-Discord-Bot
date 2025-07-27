from config import DB_FILE, ROLE_ID, GUILD_ID

import os
import time
from discord import app_commands, ui, Interaction, User, ButtonStyle, File, Forbidden, Embed, Object
from discord.ext import commands
from discord.ui import View


class AdminView(ui.View):
    def __init__(self, bot: commands.Bot, author: User):
        super().__init__(timeout=60)
        self.bot = bot
        self.author = author

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This panel is not for you.", ephemeral=True)
            return False
        return True

    @ui.button(label="Database", style=ButtonStyle.secondary, custom_id="admin_db", emoji="📦")
    async def db_btn(self, interaction: Interaction, button: ui.Button):
        if not os.path.isfile(DB_FILE):
            await interaction.response.send_message("Database file not found.", ephemeral=True)
            return
        try:
            await interaction.response.send_message("📦 Sending database file...", ephemeral=True)
            await interaction.followup.send(file=File(DB_FILE), ephemeral=True)
        except Forbidden:
            await interaction.followup.send("I can't DM you. Enable DMs from server members.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error:\n```{e}```", ephemeral=True)

    @ui.button(label="Ping", style=ButtonStyle.secondary, custom_id="admin_ping", emoji="🏓")
    async def ping_btn(self, interaction: Interaction, button: ui.Button):
        start_time = time.time()
        await interaction.response.send_message("🏓 Pinging...", ephemeral=True)
        latency = round((time.time() - start_time) * 1000)
        ws_latency = round(self.bot.latency * 1000)
        await interaction.followup.send(
            f"🏓 **Pong!**\nAPI Latency: `{latency}ms`\nWebsocket Latency: `{ws_latency}ms`", ephemeral=True
        )

    @ui.button(label="Reload Cogs", style=ButtonStyle.secondary, custom_id="admin_reload", emoji="🔄")
    async def reload_btn(self, interaction: Interaction, button: ui.Button):
        try:
            for ext in list(self.bot.extensions):
                await self.bot.reload_extension(ext)
            await interaction.response.send_message("All cogs reloaded successfully.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Failed to reload cogs:\n```{e}```", ephemeral=True)

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = DB_FILE

    @app_commands.command(name="admin", description="Admin Panel")
    @app_commands.guilds(Object(id=GUILD_ID))
    @app_commands.checks.has_role(ROLE_ID)
    async def admin(self, interaction: Interaction):
        ansi_block = (
            "```ansi\n"
            "\x1b[1;32m📦 Database\x1b[0m: Download the bot's database\n"
            "\x1b[1;33m🏓 Ping\x1b[0m: Check bot latency\n"
            "\x1b[1;34m🔄 Reload Cogs\x1b[0m: Refresh all cogs\n"
            "\x1b[1;31m⚙️ Admin tools for authorized users\x1b[0m\n"
            "```"
        )
        embed = Embed(
            title=f"{interaction.user.name}'s Admin Panel",
            description=ansi_block,
            color=0x7289DA
        )
        avatar = interaction.user.avatar.url if interaction.user.avatar else "https://i.ibb.co/ctN5fsV/leaf.png"
        embed.set_thumbnail(url=avatar)
        embed.set_footer(text="All actions are ephemeral. Only you can see them.")
        view = AdminView(self.bot, interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))