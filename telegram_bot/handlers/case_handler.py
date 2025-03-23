from aiogram import Router, types
from telegram_bot.services.cryptoapis_handler import CryptoAPIClient
from telegram_bot.utils.link_parser import parse_link
from telegram_bot.utils.logger import logger

router = Router()
crypto_client = CryptoAPIClient()

@router.message()
async def handle_message(message: types.Message):
    logger.info(f"Received message: {message.text}")

    network, txid = parse_link(message.text)
    if network and txid:
        logger.info(f"Parsed link: network={network}, txid={txid}")
        try:
            tx_data = await crypto_client.get_transaction(network, txid)
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
