<p align="center">
  <img src="https://i.ibb.co/TMnHDzL2/watchparty.png" alt="Watch2Gether Bot Logo" width="120" />
</p>

<h1 align="center">Watch2Gether Discord Bot</h1>

<p align="center">
  <a href="https://github.com/cfunkz/Watch2Gether-Discord-Bot/stargazers">
    <img src="https://img.shields.io/github/stars/cfunkz/Watch2Gether-Discord-Bot?style=social" alt="GitHub stars" />
  </a>
  <a href="https://github.com/cfunkz/Watch2Gether-Discord-Bot/network/members">
    <img src="https://img.shields.io/github/forks/cfunkz/Watch2Gether-Discord-Bot?style=social" alt="GitHub forks" />
  </a>
  <a href="https://github.com/cfunkz/Watch2Gether-Discord-Bot/issues">
    <img src="https://img.shields.io/github/issues/cfunkz/Watch2Gether-Discord-Bot" alt="GitHub issues" />
  </a>
  <a href="https://github.com/cfunkz/Watch2Gether-Discord-Bot/actions">
    <img src="https://img.shields.io/github/workflow/status/cfunkz/Watch2Gether-Discord-Bot/CI" alt="Build Status" />
  </a>
</p>

# Features
- Create new temporary rooms via Watch2Gether.
- Link existing Watch2Gether rooms.
- Validate and verify Watch2Gether URLs using **regular expressions (regex)**.
- Manage multiple rooms per user with limits.
- Add videos to playlist.
- Instant play a video.
- Download local database and reload bot cogs via admin panel.
- Uses **aiohttp** for asynchronous HTTP requests.
- Uses **aiosqlite** for asynchronous database operations, enabling concurrency.
- Employs Discord **modals**, **select menus**, and **options** for interactive user input and command handling.
- Simple Admin Panel for database management and reloading cogs.
- Custom logger
  
# Setup

**API KEY:** Get your Watch2Gether API key from your account page:  
[W2G Profile Page](https://w2g.tv/en/account/edit_user/)

**Discord Bot Token:** Create a bot on the Discord Developer Portal:  
[DISCORD API](https://discord.com/developers/applications)

```bash
git clone https://github.com/cfunkz/Watch2Gether-Discord-Bot.git
cd Watch2Gether-Discord-Bot
```

Create and activate a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows PowerShell
```

Install dependencies

```bash
pip install -r requirements.txt
```

Configure your environment

Edit `config.py` with:

```python
W2G_API_KEY = "WATCH2GETHER KEY"
BOT_TOKEN = "DISCORD TOKEN"
DB_FILE = "user_rooms.db" # Database file path
GUILD_ID = 1234567890000000001  # Your server ID
ROLE_ID = 1234567898098766554   # Admin Role ID that should have access
MAX_LOG_SIZE = 33554432  # Maximum LOG SIZE in bytes (32 MB)
ROTATE_LOGS = 5  # HOW MANY LOGS TO ROTATE
LOG_FILE = 'discord.log'
DEFAULT_AVATAR = "https://i.ibb.co/TMnHDzL2/watchparty.png"  # Default avatar URL
MAX_USER_ROOM = 10
```

Run the bot

```bash
python main.py
```

# Functions

Coming Soon

# Usage

## Admin Panel
Run `/admin` to open a private panel with buttons for:

- Downloading the database
- Checking ping
- Reloading cogs

## Manage Rooms
Use the `/watch` command to manage Watch2Gether rooms.

# Images

<p align="center">
  <img src="https://github.com/user-attachments/assets/094102d2-3c7b-4205-84f9-4748c47131e9" alt="Main" width="700" />
</p>

<table align="center">
  <tr>
    <td><img src="https://github.com/user-attachments/assets/2970cc5d-ce0c-45e9-adaa-7c4ef7c31a22" alt="Create" width="300"></td>
    <td><img src="https://github.com/user-attachments/assets/c790ec02-1804-4511-a99a-7537f998b511" alt="Add" width="300"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/16ca142b-7bd2-4b71-9875-2e7b703f9e2a" alt="Room List" width="300"></td>
    <td><img src="https://github.com/user-attachments/assets/c00c9fdf-ec81-4dcc-921a-90d919eaa0de" alt="Share Invite" width="300"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/c66de142-295c-4500-af0a-84441dda6f7c" alt="Delete Rooms" width="300"></td>
    <td><img src="https://github.com/user-attachments/assets/f51e660d-f403-4c30-bfed-6584a7221a86" alt="Admin Panel" width="300"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/1920c5db-f26a-41d6-b988-53fe8e4de4d4" alt="Add To Playlist" width="300"></td>
    <td><img src="https://github.com/user-attachments/assets/80e49491-4120-4c2b-b19d-e4778426b1f2" alt="Instant Play" width="300"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/b92ef5b0-6928-492d-b76f-65ee91d22fbb" alt="Logger" width="300"></td>
  </tr>
</table>