from config import DB_FILE

async def init_db():
    import aiosqlite
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            video_url TEXT NOT NULL,
            room_url TEXT NOT NULL,
            streamkey TEXT NOT NULL,
            is_deleted BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        await db.commit()