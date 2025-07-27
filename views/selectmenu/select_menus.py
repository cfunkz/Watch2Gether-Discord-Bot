from discord import Interaction, Embed, SelectOption, User
from typing import List
from discord.ui import Select
import aiosqlite
from config import DB_FILE
from datetime import datetime

class WatchSelect(Select):
    def __init__(self, room_data: List[dict]):
        options = [
            SelectOption(
                label=f"ID {room['id']}",
                description=(room['video_url'][:80] + "...") if len(room['video_url']) > 80 else room['video_url'],
                value=str(room['id'])
            )
            for room in room_data
        ]
        super().__init__(
            placeholder="Select rooms to delete",
            min_values=1,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: Interaction):
        user_id = str(interaction.user.id)
        room_ids = [int(rid) for rid in self.values]

        async with aiosqlite.connect(DB_FILE) as db:
            await db.executemany(
                "UPDATE rooms SET is_deleted = 1 WHERE id = ? AND user_id = ?",
                [(rid, user_id) for rid in room_ids]
            )
            await db.commit()

        await interaction.response.send_message(
            f"🗑️ Marked {len(room_ids)} room(s) as deleted.", ephemeral=True
        )

class ShareSelect(Select):
    def __init__(self, room_data: List[dict], user: User):
        self.user = user
        options = [
            SelectOption(
                label=f"ID {room['id']}",
                description=(room['video_url'][:80] + "...") if len(room['video_url']) > 80 else room['video_url'],
                value=str(room['room_url'])
            )
            for room in room_data if not room['is_deleted']
        ]
        super().__init__(
            placeholder="Select a room to share",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: Interaction):
        room_url = self.values[0]
        ansi_block = (
            "```ansi\n"
            "\x1b[1;34m🔗 {} just shared a Watch2Gether room!\x1b[0m\n"
            "\x1b[1;32m🎬 Do you wish to join them for a watch party?\x1b[0m\n"
            "```"
        ).format(self.user.name)

        embed = Embed(
            title="🌟 Room Invitation",
            description=f"[Click to join the room]({room_url})",
            color=0x00ffff
        )
        embed.add_field(name="Invite", value=ansi_block, inline=False)
        embed.set_author(name=self.user.display_name, icon_url=self.user.display_avatar.url)
        embed.set_footer(text="Shared via Watch2Gether Bot")
        embed.timestamp = datetime.now()

        await interaction.response.send_message(embed=embed, ephemeral=False)