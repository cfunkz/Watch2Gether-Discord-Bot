from discord import Interaction, Embed
from discord.ui import Modal, TextInput
from discord.ext import commands
import aiohttp
import aiosqlite
import re
from config import DB_FILE, W2G_API_KEY, MAX_USER_ROOM
from urllib.parse import urlparse


class WatchAddModal(Modal, title="Add Existing Watch2Gether Room"):
    room_url = TextInput(
        label="Room URL",
        placeholder="https://w2g.tv/rooms/... or https://w2g.tv/?r=...",
        required=True,
        max_length=200
    )

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: Interaction):
        user_id = str(interaction.user.id)
        url = self.room_url.value.strip()
        parsed = urlparse(url)
        if parsed.netloc.lower() != "w2g.tv":
            return await interaction.response.send_message("Invalid domain.", ephemeral=True)
        # Regex to match /rooms/streamkey or /?r=streamkey URLs
        pattern = re.compile(
            r'^https://w2g\.tv/(rooms/([\w-]+)|\?r=([\w-]+))$'
        )
        match = pattern.match(url)
        if not match:
            await interaction.response.send_message(
                "Wrong Watch2Gether room URL. Use 'https://w2g.tv/rooms/streamkey' or 'https://w2g.tv/?r=streamkey'.",
                ephemeral=True
            )
            return

        # Extract streamkey from URL
        streamkey = match.group(2) or match.group(3)
        if not streamkey:
            await interaction.response.send_message("Could not extract stream key from URL.", ephemeral=True)
            return

        # Verify URL with a GET request
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, allow_redirects=True) as resp:
                    if resp.status != 200:
                        await interaction.response.send_message("Room URL is not accessible (status {}).".format(resp.status), ephemeral=True)
                        return
        except aiohttp.ClientError:
            await interaction.response.send_message("Failed to verify room URL due to network error.", ephemeral=True)
            return

        # DB checks & insert
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM rooms WHERE user_id = ? AND is_deleted = 0",
                (user_id,)
            )
            count = await cursor.fetchone()
            if count is not None and count[0] >= MAX_USER_ROOM:
                await interaction.response.send_message(
                    f"You have reached the maximum of {MAX_USER_ROOM} active rooms. Delete one first.", ephemeral=True
                )
                return

            cursor = await db.execute(
                "SELECT id FROM rooms WHERE user_id = ? AND streamkey = ? AND is_deleted = 0",
                (user_id, streamkey)
            )
            if await cursor.fetchone():
                await interaction.response.send_message("This room is already in your list.", ephemeral=True)
                return

            await db.execute(
                "INSERT INTO rooms (user_id, video_url, room_url, streamkey, is_deleted) VALUES (?, ?, ?, ?, 0)",
                (user_id, "`Linked Room`", url, streamkey)
            )
            await db.commit()

        embed = Embed(
            title="Room Added ✅",
            description=f"[Click to join]({url})",
            color=0x2ecc71
        )
        embed.add_field(name="Room URL", value=url, inline=False)
        embed.set_footer(text="Added to your list.")
        embed.set_thumbnail(url=interaction.user.display_avatar.replace(format='png').url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class WatchCreateModal(Modal, title="Create Watch2Gether Room"):
    video_url = TextInput(
        label="Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        required=True,
        max_length=200
    )
    bg_color = TextInput(
        label="Background color (Hex)",
        placeholder="#000000",
        required=False,
        max_length=7,
        default="#000000"
    )
    bg_opacity = TextInput(
        label="Background opacity (0-100)",
        placeholder="50",
        required=False,
        max_length=3,
        default="50"
    )

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: Interaction):
        user_id = str(interaction.user.id)

        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM rooms WHERE user_id = ? AND is_deleted = 0",
                (user_id,)
            )
            count = await cursor.fetchone()
            if count is not None and count[0] >= MAX_USER_ROOM:
                await interaction.response.send_message(
                    f"You have reached the maximum of {MAX_USER_ROOM} active rooms. Delete one first.", ephemeral=True
                )
                return

        if not self.video_url.value.startswith(("http://", "https://")):
            await interaction.response.send_message("Invalid video URL.", ephemeral=True)
            return

        bg_color = self.bg_color.value.strip()
        if not (bg_color.startswith("#") and len(bg_color) == 7 and all(c in "0123456789abcdefABCDEF" for c in bg_color[1:])):
            bg_color = "#000000"

        try:
            opacity = int(self.bg_opacity.value)
            if not (0 <= opacity <= 100):
                opacity = 50
        except ValueError:
            opacity = 50

        payload = {
            "w2g_api_key": W2G_API_KEY,
            "share": self.video_url.value,
            "bg_color": bg_color,
            "bg_opacity": str(opacity)
        }

        async with aiohttp.ClientSession() as session:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            try:
                async with session.post("https://api.w2g.tv/rooms/create.json", json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        await interaction.response.send_message(
                            "Failed to create room (external API error).", ephemeral=True
                        )
                        return
                    data = await resp.json()
            except aiohttp.ClientError:
                await interaction.response.send_message(
                    "Failed to contact Watch2Gether API.", ephemeral=True
                )
                return

        streamkey = data.get("streamkey")
        if not streamkey:
            await interaction.response.send_message("Failed to create room (no streamkey).", ephemeral=True)
            return

        room_url = f"https://w2g.tv/rooms/{streamkey}"

        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute(
                "INSERT INTO rooms (user_id, video_url, room_url, streamkey, is_deleted) VALUES (?, ?, ?, ?, 0)",
                (user_id, self.video_url.value, room_url, streamkey)
            )
            await db.commit()

        embed = Embed(
            title="Room Created ✅",
            description=f"[Click to join]({room_url})",
            color=0x2ecc71
        )
        embed.add_field(name="Video URL", value=self.video_url.value, inline=False)
        embed.set_footer(text="Saved to your list.")
        embed.set_thumbnail(url=interaction.user.display_avatar.replace(format='png').url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        
class AddUrlModal(Modal, title="Add URL to Watch2Gether Room"):
    url = TextInput(
        label="Video URL (YouTube, Twitch, etc.)",
        placeholder="https://www.youtube.com/watch?v=...",
        required=True,
        max_length=200
    )

    def __init__(self, mode: str, streamkey: str):
        super().__init__()
        self.mode = mode  # "playlist" or "insta_play"
        self.streamkey = streamkey

    async def on_submit(self, interaction: Interaction):
        url = self.url.value.strip()
        # Simple regex check for supported URLs (expand as needed)
        patterns = [
            r'https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://youtu\.be/[\w-]+',
            r'https?://(www\.)?twitch\.tv/[\w-]+',
            # add more supported regexes here...
        ]
        if not any(re.match(pattern, url) for pattern in patterns):
            await interaction.response.send_message("URL is not supported or invalid.", ephemeral=True)
            return

        api_key = W2G_API_KEY
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        async with aiohttp.ClientSession() as session:
            if self.mode == "playlist":
                # Add to playlist API call
                api_url = f"https://api.w2g.tv/rooms/{self.streamkey}/playlists/current/playlist_items/sync_update"
                payload = {
                    "w2g_api_key": api_key,
                    "add_items": [{"url": url, "title": "Added via Bot"}]
                }
            else:
                # Insta play API call
                api_url = f"https://api.w2g.tv/rooms/{self.streamkey}/sync_update"
                payload = {
                    "w2g_api_key": api_key,
                    "item_url": url
                }

            try:
                async with session.post(api_url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        action = "added to playlist" if self.mode == "playlist" else "playing now"
                        await interaction.response.send_message(f"Successfully {action} in the room!", ephemeral=True)
                    else:
                        text = await resp.text()
                        await interaction.response.send_message(f"API error: {resp.status} {text}", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Failed to contact Watch2Gether API: {e}", ephemeral=True)
