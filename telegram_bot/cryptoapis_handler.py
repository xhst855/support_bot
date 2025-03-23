import requests
import os
from logger import setup_logger

logger = setup_logger()

API_KEY = os.getenv("CRYPTOAPIS_API_KEY")
BASE_URL = "https://rest.cryptoapis.io/v2"

# Сопоставление сетей
NETWORK_MAPPING = {
    "ETH": {"blockchain": "ethereum", "network": "mainnet"},
    "BSC": {"blockchain": "bsc", "network": "mainnet"},
    "BTC": {"blockchain": "bitcoin", "network": "mainnet"},
    "LTC": {"blockchain": "litecoin", "network": "mainnet"},
    "TRON": {"blockchain": "tron", "network": "mainnet"},
    "POLYGON": {"blockchain": "polygon", "network": "mainnet"},
}

# Известные контракты токенов (можно расширять)
TOKEN_CONTRACTS = {
    "ETH": ["0xdac17f958d2ee523a2206206994597c13d831ec7"],  # USDT ERC-20
    "BSC": ["0x55d398326f99059ff775485246999027b3197955"],  # USDT BEP-20
    "POLYGON": ["0x3813e82e6f7098b9583FC0F33a962D02018B6803"]  # USDT Polygon (пример)
}

def get_transaction_details(network, txid):
    mapping = NETWORK_MAPPING.get(network)
    if not mapping:
        return {"error": f"Сеть {network} не поддерживается."}

    blockchain = mapping["blockchain"]
    net = mapping["network"]

    headers = {"X-API-Key": API_KEY}

    # --- Step 1: Basic transaction request ---
    tx_url = f"{BASE_URL}/blockchain-data/{blockchain}/{net}/transactions/{txid}"
    logger.info(f"Пробуем основной запрос: {tx_url}")

    try:
        response = requests.get(tx_url, headers=headers)
        logger.info(f"Crypto APIs Basic Tx Response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            data = response.json().get("data", {}).get("item", {})
            amount = data.get("transactionAmount", "N/A")
            recipients = data.get("recipients", [])
            recipient = recipients[0].get("address", "N/A") if recipients else "N/A"
            status = data.get("status", "N/A")
            return {"amount": amount, "to": recipient, "status": status}
        elif response.status_code == 400 and blockchain in ["ethereum", "bsc", "polygon"]:
            logger.warning("Обычная транзакция не найдена, пробуем токен.")
            # --- Step 2: Try token transactions ---
            for contract in TOKEN_CONTRACTS.get(network, []):
                token_url = f"{BASE_URL}/blockchain-data/{blockchain}/{net}/tokens/{contract}/transactions/{txid}"
                logger.info(f"Пробуем запрос к токену: {token_url}")
                token_response = requests.get(token_url, headers=headers)
                logger.info(f"Crypto APIs Token Tx Response: {token_response.status_code} - {token_response.text}")

                if token_response.status_code == 200:
                    token_data = token_response.json().get("data", {}).get("item", {})
                    amount = token_data.get("transactionAmount", "N/A")
                    recipients = token_data.get("recipients", [])
                    recipient = recipients[0].get("address", "N/A") if recipients else "N/A"
                    status = token_data.get("status", "N/A")
                    return {"amount": amount, "to": recipient, "status": status}

        # Если ничего не нашли:
        return {"error": f"Ошибка {response.status_code}: {response.text}"}
    except Exception as e:
        logger.error(f"Ошибка запроса к Crypto APIs: {e}")
        return {"error": str(e)}
