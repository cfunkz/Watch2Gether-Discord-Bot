
from discord import Interaction, User, Embed, ButtonStyle
from discord.ext import commands
from discord.ui import View, button, Button
import aiosqlite
from config import DB_FILE
from datetime import datetime
from views.modal.modals import WatchCreateModal, WatchAddModal
from views.selectmenu.select_menus import WatchSelect, ShareSelect

class WatchView(View):
    def __init__(self, bot: commands.Bot, author: User):
        super().__init__(timeout=60)
        self.bot = bot
        self.author = author

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This menu is not for you.", ephemeral=True)
            return False
        return True

    @button(label="Create", style=ButtonStyle.secondary, custom_id="watch_create", emoji="➕")
    async def create_btn(self, interaction: Interaction, button: Button):
        modal = WatchCreateModal(self.bot)
        await interaction.response.send_modal(modal)

    @button(label="Add", style=ButtonStyle.secondary, custom_id="watch_add", emoji="🔗")
    async def add_btn(self, interaction: Interaction, button: Button):
        modal = WatchAddModal(self.bot)
        await interaction.response.send_modal(modal)

    @button(label="List", style=ButtonStyle.secondary, custom_id="watch_list", emoji="📜")
    async def list_btn(self, interaction: Interaction, button: Button):
        user_id = str(interaction.user.id)
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT id, video_url, room_url, created_at FROM rooms WHERE user_id = ? AND is_deleted = 0 ORDER BY created_at DESC",
                (user_id,)
            )
            rows = list(await cursor.fetchall())

        if not rows:
            return await interaction.response.send_message("You have no active rooms.", ephemeral=True)

        embed = Embed(
            title=f"{interaction.user.name}'s Watch2Gether Rooms",
            color=0x1abc9c,
            timestamp=datetime.now()
        )
        for room_id, video_url, room_url, created_at in rows:
            dt_obj = datetime.fromisoformat(created_at)
            timestamp = int(dt_obj.timestamp())
            time_str = f"<t:{timestamp}:f>"
            display_url = (video_url[:55] + "...") if len(video_url) > 58 else video_url
            embed.add_field(
                name=f"🎥 Room ID {room_id} — {time_str}",
                value=f"[Join Room]({room_url})\n🔗 {display_url}",
                inline=False
            )
        embed.set_footer(text=f"Total rooms: {len(rows)}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @button(label="Share", style=ButtonStyle.secondary, custom_id="watch_share", emoji="📤")
    async def share_btn(self, interaction: Interaction, button: Button):
        user_id = str(interaction.user.id)
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT id, video_url, room_url, is_deleted FROM rooms WHERE user_id = ? AND is_deleted = 0",
                (user_id,)
            )
            rows = await cursor.fetchall()

        if not rows:
            return await interaction.response.send_message("You have no active rooms to share.", ephemeral=True)

        room_data = [{"id": r[0], "video_url": r[1], "room_url": r[2], "is_deleted": r[3]} for r in rows]
        view = View()
        view.add_item(ShareSelect(room_data, interaction.user))
        await interaction.response.send_message(
            "📤 Pick a room to share with others:",
            view=view,
            ephemeral=True
        )

    @button(label="Delete", style=ButtonStyle.secondary, custom_id="watch_delete", emoji="🗑️")
    async def delete_btn(self, interaction: Interaction, button: Button):
        user_id = str(interaction.user.id)
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT id, video_url FROM rooms WHERE user_id = ? AND is_deleted = 0",
                (user_id,)
            )
            rows = await cursor.fetchall()

        if not rows:
            return await interaction.response.send_message("You have no active rooms to delete.", ephemeral=True)

        room_data = [{"id": r[0], "video_url": r[1]} for r in rows]
        view = View()
        view.add_item(WatchSelect(room_data))
        await interaction.response.send_message(
            "Select rooms to delete:",
            view=view,
            ephemeral=True
        )
