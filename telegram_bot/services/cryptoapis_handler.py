import httpx
from tenacity import retry, wait_exponential, stop_after_attempt
from telegram_bot.utils.logger import logger
from telegram_bot.config import settings

class CryptoAPIClient:
    def __init__(self):
        self.base_url = "https://rest.cryptoapis.io/v2/blockchain-data"
        self.api_key = settings.CRYPTOAPIS_KEY
        self.headers = {"X-API-Key": self.api_key}
        self.timeout = 10

    @retry(wait=wait_exponential(min=2, max=10), stop=stop_after_attempt(3))
    async def get_transaction(self, network, txid):
        url = f"{self.base_url}/{network}/transactions/{txid}"
        logger.info(f"Requesting CryptoAPI: {url}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
        logger.info(f"Response: {response.status_code} {response.text}")
        if response.status_code == 404 and "evm" in network:
            return await self.get_token_transaction(network, txid)
        response.raise_for_status()
        return response.json()

    async def get_token_transaction(self, network, txid):
        url = f"{self.base_url}/{network}/tokens/transactions/{txid}"
        logger.info(f"Fallback request: {url}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
        logger.info(f"Fallback response: {response.status_code} {response.text}")
        response.raise_for_status()
        return response.json()
