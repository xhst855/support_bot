import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from categorize_bert import categorize_message
from desk import create_ticket, add_comment
from telegram_bot.utils.logger import setup_logger
from db import init_db, save_ticket, get_ticket_by_message
from aiogram.exceptions import TelegramAPIError
from telegram_bot.handlers.case_handler import handle_case

logger = setup_logger()

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Здравствуйте! Напишите свой вопрос.")

# Создание тикета для новых сообщений
@dp.message(F.chat.type.in_({"group", "supergroup"}), ~F.reply_to_message)
async def handle_group_message(message: types.Message):
    if message.from_user.is_bot:
        return

    logger.info(f"New ticket from group {message.chat.id}: {message.text}")

    try:
        # Сначала определяем кейс по шаблону (txid и т.д.)
        case_result = handle_case(message.text)
        logger.info(f"Определён кейс: {case_result['case']}, действие: {case_result['action']}")

        # Если найдена транзакция или адрес, сразу отправляем пользователю ответ
        await message.reply(case_result["response"])

        # После этого категоризация BERT'ом
        category = categorize_message(message.text)
        logger.info(f"Категория для сообщения '{message.text}': {category}")

        # Создание тикета
        ticket_id = create_ticket(message.chat.id, message.text, category)

        if ticket_id:
            save_ticket(message.message_id, ticket_id)  # Сохраняем связь
            await message.reply(f"✅ Тикет №{ticket_id} создан в категории '{category}'. Отвечайте на это сообщение, чтобы добавить комментарий.")
            logger.info(f"Ticket {ticket_id} created successfully for group chat {message.chat.id}.")
        else:
            await message.reply("❌ Ошибка при создании тикета.")
            logger.error(f"Failed to create ticket for group chat {message.chat.id}.")

    except Exception as e:
        logger.exception(f"Unexpected error in group chat: {e}")
        await message.reply("⚠️ Произошла ошибка. Мы уже разбираемся.")

# Добавляем комментарий в тикет для реплаев
@dp.message(F.chat.type.in_({"group", "supergroup"}), F.reply_to_message)
async def handle_reply_message(message: types.Message):
    if message.from_user.is_bot:
        return

    original_message_id = message.reply_to_message.message_id
    ticket_id = get_ticket_by_message(original_message_id)

    if ticket_id:
        logger.info(f"Adding comment to ticket {ticket_id} from message: {message.text}")

        try:
            success = add_comment(ticket_id, message.text)
            if success:
                await message.reply(f"💬 Сообщение добавлено в тикет №{ticket_id}.")
                logger.info(f"Comment added to ticket {ticket_id}.")
            else:
                await message.reply("❌ Ошибка при добавлении комментария.")
                logger.error(f"Failed to add comment to ticket {ticket_id}.")

        except Exception as e:
            logger.exception(f"Error while adding comment: {e}")
            await message.reply("⚠️ Произошла ошибка при добавлении комментария.")
    else:
        await message.reply("⚠️ Не удалось найти тикет для этого сообщения.")

async def main():
    init_db()  # Инициализация БД
    logger.info("Starting Telegram Bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
