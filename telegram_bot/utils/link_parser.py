import re

EXPLORER_PATTERNS = {
    "ethereum": r"https?://(www\.)?(etherscan\.io|bscscan\.com)/tx/(?P<txid>[0-9a-zA-Z]+)",
    "oklink": r"https?://www\.oklink\.com/(?P<network>[a-zA-Z0-9\-]+)/tx/(?P<txid>[0-9a-zA-Z]+)",
    # Добавим больше по мере необходимости
}

def parse_link(message: str):
    for network, pattern in EXPLORER_PATTERNS.items():
        match = re.search(pattern, message)
        if match:
            txid = match.group("txid")
            return network, txid
    return None, None
