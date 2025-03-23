from aiogram import Router, types
from telegram_bot.services.cryptoapis_handler import CryptoAPIClient
from telegram_bot.utils.link_parser import parse_link
from telegram_bot.utils.logger import logger
import unicodedata

router = Router()
crypto_client = CryptoAPIClient()

def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace('\n', ' ').replace('\u200b', '').replace('\u00ad', '').strip()
    return text.lower()

@router.message()
async def handle_transaction(message: types.Message):
    logger.info(f"Received message: {message.text}")

    cleaned_text = clean_text(message.text)
    logger.info(f"Cleaned message: {cleaned_text}")

    network, txid = parse_link(cleaned_text)
    if network and txid:
        logger.info(f"Parsed link: network={network}, txid={txid}")
        try:
            tx_data = await crypto_client.get_transaction(network, txid)
            logger.info(f"Transaction data received: {tx_data}")

            # Универсальная обработка токеновых трансферов (EVM + TRON)
            if "items" in tx_data.get("data", {}):
                item = tx_data["data"]["items"][0]
                recipient = item.get("recipient")
                sender = item.get("sender")
                token_data = item.get("tokenData", {})
                token = token_data.get("symbol", "N/A")
                amount = token_data.get("fungibleValues", {}).get("amount", "N/A")

                reply_text = (
                    f"🔄 Token Transfer:\n"
                    f"Token: {token}\n"
                    f"Amount: {amount} {token}\n"
                    f"Sender: {sender}\n"
                    f"Recipient: {recipient}\n"
                    f"TxID: {txid}"
                )
            else:
                # Обычные транзакции (UTXO, EVM native)
                tx_info = tx_data.get('data', {}).get('item', {})
                reply_text = (
                    f"🔎 Transaction Info:\n"
                    f"Network: {network}\n"
                    f"TxID: {txid}\n"
                    f"Status: {tx_info.get('status', 'N/A')}\n"
                    f"Amount: {tx_info.get('amount', 'N/A')}\n"
                    f"Recipient: {tx_info.get('recipient', {}).get('address', 'N/A')}\n"
                )

            await message.reply(reply_text)

        except Exception as e:
            logger.exception(f"Error processing transaction: {e}")
            await message.reply("❌ Не удалось получить информацию по транзакции. Попробуйте позже.")
    else:
        logger.info("No valid blockchain link found in message.")
        await message.reply("Ссылка на транзакцию не обнаружена.")
