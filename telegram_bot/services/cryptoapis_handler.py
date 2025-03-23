import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from telegram_bot.config import settings

logger = logging.getLogger("support_bot")

class CryptoAPIClient:
    def __init__(self):
        self.base_url = "https://rest.cryptoapis.io/v2"
        self.headers = {
            "X-API-Key": settings.CRYPTOAPIS_KEY
        }

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def get_transaction(self, network, txid):
        url = f"{self.base_url}/transactions/evm/{network}/mainnet/{txid}"
        logger.info(f"Requesting CryptoAPI: {url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            logger.info(f"Response: {response.status_code} {response.text}")
            if response.status_code == 404 or response.status_code == 400:
                # Fallback for token transfers
                return await self.get_token_transaction(network, txid)
            response.raise_for_status()
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def get_token_transaction(self, network, txid):
        url = f"{self.base_url}/transactions/evm/{network}/mainnet/{txid}/tokens-transfers"
        logger.info(f"Fallback request (token transfer): {url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            logger.info(f"Fallback response: {response.status_code} {response.text}")
            response.raise_for_status()
            return response.json()
