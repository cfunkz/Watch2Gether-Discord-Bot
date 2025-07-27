# Use official Python 3.13.1 slim image as base
FROM python:3.13.1-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variables if you want to set them here instead of config.py
# ENV W2G_API_KEY=your_watch2gether_api_key
# ENV BOT_TOKEN=your_discord_bot_token
# ENV DB_FILE=user_rooms.db
# ENV GUILD_ID=1234567890000000001
# ENV ROLE_ID=1234567898098766554

# Run the bot
CMD ["python", "main.py"]