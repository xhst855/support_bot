from aiogram import Router, types
from telegram_bot.services.desk_service import ZohoDeskClient
from telegram_bot.utils.logger import logger

router = Router()
desk_client = ZohoDeskClient()

@router.message()
async def handle_message(message: types.Message):
    logger.info(f"Processing message from user {message.from_user.id}: {message.text}")

    try:
        if message.reply_to_message:
            ticket_id = await desk_client.get_ticket_id_by_message(message.reply_to_message.message_id)
            if ticket_id:
                await desk_client.add_comment(ticket_id, message.text)
                await message.reply(f"Комментарий добавлен к тикету #{ticket_id}")
            else:
                await message.reply("⚠️ Не найден связанный тикет для комментария.")
        else:
            ticket_id = await desk_client.create_ticket(message.from_user.id, message.text)
            await desk_client.save_message_ticket_link(message.message_id, ticket_id)
            await message.reply(f"🎟️ Тикет #{ticket_id} создан.")
    except Exception as e:
        logger.exception(f"Error processing Zoho Desk action: {e}")
        await message.reply("❌ Ошибка при работе с тикетами. Пожалуйста, попробуйте позже.")
