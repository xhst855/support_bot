import re
from cryptoapis_handler import get_transaction_details
from logger import setup_logger

logger = setup_logger()

# Регулярное выражение для извлечения ссылки
LINK_REGEX = re.compile(
    r"https?://(?:www\.)?(?P<explorer>[\w\.]+)(?:/[\w\-]+)?/(?P<network>\w+)/tx/(?P<txid>[A-Fa-f0-9x]+)",
    re.IGNORECASE
)


def handle_case(message_text):
    result = {"case": None, "action": None, "response": None}

    logger.info(f"Проверка сообщения: {message_text}")

    link_match = LINK_REGEX.search(message_text)
    if link_match:
        network = link_match.group("network").upper()
        txid = link_match.group("txid")

        logger.info(f"Найдена ссылка на транзакцию. Сеть: {network}, TxID: {txid}")

        # Получаем детали транзакции
        tx_details = get_transaction_details(network, txid)
        logger.info(f"Данные транзакции: {tx_details}")

        if "error" in tx_details:
            result["case"] = "TxidNotFound"
            result["response"] = f"❌ Ошибка получения транзакции: {tx_details['error']}"
            logger.warning(f"Ошибка получения транзакции: {tx_details['error']}")
        else:
            result["case"] = "CheckTxid"
            result["action"] = "check_transaction"
            result["response"] = (
                f"✅ Найдена транзакция!\n\n"
                f"Сеть: {network}\n"
                f"TxID: {txid}\n"
                f"Статус: {tx_details['status']}\n"
                f"Получатель: {tx_details['to']}\n"
                f"Сумма: {tx_details['amount']}"
            )
    else:
        logger.info("Ссылка на транзакцию не найдена в сообщении.")
        result["case"] = "NoTxidFound"
        result["response"] = "Не удалось определить транзакцию в сообщении. Передали оператору."

    return result
