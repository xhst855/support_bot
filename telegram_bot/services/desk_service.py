import httpx
from tenacity import retry, wait_exponential, stop_after_attempt
from telegram_bot.utils.logger import logger
from telegram_bot.config import settings
from telegram_bot.services.db import DBClient  # Для сохранения связей

class ZohoDeskClient:
    def __init__(self):
        self.api_base = "https://desk.zoho.com/api/v1"
        self.access_token = None
        self.db = DBClient()

    async def refresh_token(self):
        logger.info("Refreshing Zoho Desk token...")
        url = "https://accounts.zoho.com/oauth/v2/token"
        params = {
            "refresh_token": settings.ZOHO_REFRESH_TOKEN,
            "client_id": settings.ZOHO_CLIENT_ID,
            "client_secret": settings.ZOHO_CLIENT_SECRET,
            "grant_type": "refresh_token"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, params=params)
        resp.raise_for_status()
        self.access_token = resp.json()["access_token"]
        logger.info("Zoho Desk token refreshed.")

    def headers(self):
        return {"Authorization": f"Zoho-oauthtoken {self.access_token}"}

    @retry(wait=wait_exponential(min=2, max=10), stop=stop_after_attempt(3))
    async def create_ticket(self, user_id, message_text):
        if not self.access_token:
            await self.refresh_token()
        url = f"{self.api_base}/tickets"
        data = {
            "subject": f"Message from Telegram user {user_id}",
            "departmentId": "YOUR_DEPARTMENT_ID",
            "description": message_text,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=data, headers=self.headers())
        if resp.status_code == 401:
            await self.refresh_token()
            return await self.create_ticket(user_id, message_text)
        resp.raise_for_status()
        ticket_id = resp.json()["id"]
        logger.info(f"Ticket #{ticket_id} created.")
        return ticket_id

    @retry(wait=wait_exponential(min=2, max=10), stop=stop_after_attempt(3))
    async def add_comment(self, ticket_id, comment):
        if not self.access_token:
            await self.refresh_token()
        url = f"{self.api_base}/tickets/{ticket_id}/comments"
        data = {"content": comment, "isPublic": True}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=data, headers=self.headers())
        if resp.status_code == 401:
            await self.refresh_token()
            return await self.add_comment(ticket_id, comment)
        resp.raise_for_status()
        logger.info(f"Comment added to ticket #{ticket_id}.")

    async def save_message_ticket_link(self, message_id, ticket_id):
        await self.db.save_link(message_id, ticket_id)

    async def get_ticket_id_by_message(self, message_id):
        return await self.db.get_ticket_id(message_id)
