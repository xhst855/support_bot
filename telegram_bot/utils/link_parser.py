import re
from telegram_bot.utils.logger import logger

EXPLORER_PATTERNS = {
    "oklink": r"https?://www\.oklink\.com(/[\w\-]+){0,2}/(?P<network>[a-zA-Z0-9\-]+)/tx/(?P<txid>[0-9a-fA-F]+)",
    "etherscan": r"https?://(www\.)?(etherscan\.io|bscscan\.com|polygonscan\.com)/tx/(?P<txid>0x[a-fA-F0-9]+)",
}

# Маппинг названий сетей в формат CryptoAPI
NETWORK_MAP = {
    "eth": "ethereum",
    "ethereum": "ethereum",
    "bsc": "bsc",
    "binance-smart-chain": "bsc",
    "polygon": "polygon",
    "matic": "polygon",
    "btc": "bitcoin",
    "bitcoin": "bitcoin",
    "trx": "tron",
    "tron": "tron",
}

def parse_link(message: str):
    cleaned = message.replace('\n', ' ').replace('\u200b', '').replace('\u00ad', '').strip().lower()
    logger.info(f"Cleaned message for parsing: {cleaned}")

    for explorer, pattern in EXPLORER_PATTERNS.items():
        logger.info(f"Trying pattern for {explorer}: {pattern}")
        match = re.search(pattern, cleaned)
        if match:
            txid = match.group("txid")
            raw_network = match.groupdict().get("network")
            logger.info(f"Match found: explorer={explorer}, raw_network={raw_network}, txid={txid}")
            if raw_network:
                mapped_network = NETWORK_MAP.get(raw_network.lower(), raw_network.lower())
            else:
                if "etherscan" in explorer:
                    mapped_network = "ethereum"
                else:
                    mapped_network = explorer
            logger.info(f"Mapped network for CryptoAPI: {mapped_network}")
            return mapped_network, txid
        else:
            logger.info(f"No match for {explorer} pattern.")

    logger.info("No valid blockchain link found after checking all patterns.")
    return None, None
