import aiosqlite
from telegram_bot.utils.logger import logger
from telegram_bot.config import settings

class DBClient:
    def __init__(self):
        self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")

    async def save_link(self, message_id, ticket_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS message_ticket (message_id INTEGER PRIMARY KEY, ticket_id TEXT)"
            )
            await db.execute(
                "INSERT OR REPLACE INTO message_ticket (message_id, ticket_id) VALUES (?, ?)",
                (message_id, ticket_id),
            )
            await db.commit()
            logger.info(f"Saved link: message_id={message_id} <-> ticket_id={ticket_id}")

    async def get_ticket_id(self, message_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS message_ticket (message_id INTEGER PRIMARY KEY, ticket_id TEXT)"
            )
            cursor = await db.execute(
                "SELECT ticket_id FROM message_ticket WHERE message_id = ?", (message_id,)
            )
            row = await cursor.fetchone()
            ticket_id = row[0] if row else None
            logger.info(f"Fetched ticket_id={ticket_id} for message_id={message_id}")
            return ticket_id
