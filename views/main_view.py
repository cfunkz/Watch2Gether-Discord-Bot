
from discord import Interaction, User, Embed, ButtonStyle, SelectOption
from discord.ext import commands
from discord.ui import View, button, Button, Select
import aiosqlite
from config import DB_FILE
from datetime import datetime
from views.modal.modals import WatchCreateModal, WatchAddModal, AddUrlModal
from views.selectmenu.select_menus import WatchSelect, ShareSelect

class WatchView(View):
    def __init__(self, bot: commands.Bot, author: User):
        super().__init__(timeout=120)
        self.bot = bot
        self.author = author

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This menu is not for you.", ephemeral=True)
            return False
        return True

    @button(label="Create", style=ButtonStyle.secondary, custom_id="watch_create", emoji="🆕")
    async def create_btn(self, interaction: Interaction, button: Button):
        modal = WatchCreateModal(self.bot)
        await interaction.response.send_modal(modal)

    @button(label="Link", style=ButtonStyle.secondary, custom_id="watch_add", emoji="🔗")
    async def add_btn(self, interaction: Interaction, button: Button):
        modal = WatchAddModal(self.bot)
        await interaction.response.send_modal(modal)

    @button(label="List", style=ButtonStyle.secondary, custom_id="watch_list", emoji="📋")
    async def list_btn(self, interaction: Interaction, button: Button):
        user_id = str(interaction.user.id)
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT id, video_url, room_url, created_at FROM rooms WHERE user_id = ? AND is_deleted = 0 ORDER BY created_at DESC",
                (user_id,)
            )
            rows = list(await cursor.fetchall())

        if not rows:
            return await interaction.response.send_message("```You have no active rooms.```", ephemeral=True)

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

    @button(label="Share", style=ButtonStyle.secondary, custom_id="watch_share", emoji="👤")
    async def share_btn(self, interaction: Interaction, button: Button):
        user_id = str(interaction.user.id)
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT id, video_url, room_url, is_deleted FROM rooms WHERE user_id = ? AND is_deleted = 0",
                (user_id,)
            )
            rows = await cursor.fetchall()

        if not rows:
            return await interaction.response.send_message("```You have no active rooms to share.```", ephemeral=True)

        room_data = [{"id": r[0], "video_url": r[1], "room_url": r[2], "is_deleted": r[3]} for r in rows]
        view = View()
        view.add_item(ShareSelect(room_data, interaction.user))
        await interaction.response.send_message(
            "```📤 Pick a room to share with others:```",
            view=view,
            ephemeral=True
        )

    @button(label="Delete", style=ButtonStyle.danger, custom_id="watch_delete", emoji="🗑️")
    async def delete_btn(self, interaction: Interaction, button: Button):
        user_id = str(interaction.user.id)
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT id, video_url FROM rooms WHERE user_id = ? AND is_deleted = 0",
                (user_id,)
            )
            rows = await cursor.fetchall()

        if not rows:
            return await interaction.response.send_message("```You have no active rooms to delete.```", ephemeral=True)

        room_data = [{"id": r[0], "video_url": r[1]} for r in rows]
        view = View()
        view.add_item(WatchSelect(room_data))
        await interaction.response.send_message(
            "Select rooms to delete:",
            view=view,
            ephemeral=True
        )
        
    @button(label="Add To Playlist", style=ButtonStyle.secondary, custom_id="watch_add_to_playlist", emoji="➕")
    async def add_to_playlist_btn(self, interaction: Interaction, button: Button):
        await self.show_room_select(interaction, mode="playlist")

    @button(label="Insta Play", style=ButtonStyle.secondary, custom_id="watch_insta_play", emoji="▶️")
    async def insta_play_btn(self, interaction: Interaction, button: Button):
        await self.show_room_select(interaction, mode="insta_play")

    async def show_room_select(self, interaction: Interaction, mode: str):
        user_id = str(interaction.user.id)
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT id, room_url, streamkey FROM rooms WHERE user_id = ? AND is_deleted = 0 ORDER BY created_at DESC",
                (user_id,)
            )
            rooms = await cursor.fetchall()

        if not rooms:
            return await interaction.response.send_message("```You have no active rooms.```", ephemeral=True)

        options = [
            SelectOption(
                label=f"Room ID {r[0]}",
                description=r[1],
                value=r[2]  # streamkey as value
            ) for r in rooms
        ]

        class RoomSelect(Select):
            def __init__(self, options, mode):
                super().__init__(placeholder="Select a room", min_values=1, max_values=1, options=options)
                self.mode = mode

            async def callback(self, interaction: Interaction):
                streamkey = self.values[0]
                modal = AddUrlModal(self.mode, streamkey)
                await interaction.response.send_modal(modal)

        view = View()
        view.add_item(RoomSelect(options, mode))
        await interaction.response.send_message(f"```Select a room for {mode.replace('_', ' ')}:```", view=view, ephemeral=True)