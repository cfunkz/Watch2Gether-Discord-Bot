from discord import Interaction, Embed
from discord.ext import commands
from discord import app_commands
from views.main_view import WatchView
from config import DEFAULT_AVATAR

class WatchCog(commands.Cog):
    """Cog to manage Watch2Gether rooms"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="watch", description="Manage Watch2Gether rooms")
    @app_commands.checks.cooldown(1, 3, key=lambda i: i.user.id)
    async def watch(self, interaction: Interaction):
        if interaction.guild is None:
            return await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
        description_text = (
            "Hey there!\n"
            "Ready to kick back and watch together?\n"
            "Use the buttons below to start a room or jump right in."
        )
        # ANSI block
        ansi_block = (
            "```ansi\n"
            "\x1b[1;33mHave fun, and don’t forget the popcorn! 🍿\x1b[0m\n"
            "```"
        )
        embed = Embed(
            title=f"{interaction.user.display_name}'s Rooms",
            description=description_text,
            color=0x7289DA
        )
        embed.add_field(name="\u200b", value=ansi_block, inline=False)
        avatar = interaction.user.avatar.url if interaction.user.avatar else DEFAULT_AVATAR
        embed.set_thumbnail(url=avatar)
        embed.set_footer(text="All actions are ephemeral, apart from sharing rooms.")
        view = WatchView(self.bot, interaction.user)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(WatchCog(bot))