import sys
import asyncio
import signal
from handlers.commands import (
    handle_start, handle_help, handle_health,
    handle_scores, handle_labs, handle_unknown
)


def handle_test(command: str) -> str:
    parts = command.strip().split()
    cmd = parts[0].lower()

    if cmd == "/start":
        return handle_start()
    elif cmd == "/help":
        return handle_help()
    elif cmd == "/health":
        return handle_health()
    elif cmd == "/scores":
        lab = parts[1] if len(parts) > 1 else ""
        return handle_scores(lab)
    elif cmd == "/labs":
        return handle_labs()
    elif cmd.startswith("/"):
        return handle_unknown(command)
    else:
        from services.llm import route
        return route(command)


async def main():
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
    from config import BOT_TOKEN

    async def start(update, context):
        keyboard = [
            [
                InlineKeyboardButton("🏥 Health", callback_data="health"),
                InlineKeyboardButton("📚 Labs", callback_data="labs"),
            ],
            [
                InlineKeyboardButton("📊 Scores lab-04", callback_data="scores_lab-04"),
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(handle_start(), reply_markup=reply_markup)

    async def help_cmd(update, context):
        await update.message.reply_text(handle_help())

    async def health(update, context):
        await update.message.reply_text(handle_health())

    async def labs(update, context):
        await update.message.reply_text(handle_labs())

    async def scores(update, context):
        lab = context.args[0] if context.args else ""
        await update.message.reply_text(handle_scores(lab))

    async def handle_text(update, context):
        text = update.message.text
        from services.llm import route
        response = route(text)
        await update.message.reply_text(response)

    async def handle_button(update, context):
        query = update.callback_query
        await query.answer()
        data = query.data
        if data == "health":
            text = handle_health()
        elif data == "labs":
            text = handle_labs()
        elif data.startswith("scores_"):
            lab = data.replace("scores_", "")
            text = handle_scores(lab)
        elif data == "help":
            text = handle_help()
        else:
            text = handle_unknown(data)
        await query.edit_message_text(text)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("labs", labs))
    app.add_handler(CommandHandler("scores", scores))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is running...")
    async with app:
        await app.start()
        await app.updater.start_polling()
        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, stop_event.set)
        loop.add_signal_handler(signal.SIGINT, stop_event.set)
        await stop_event.wait()
        await app.updater.stop()
        await app.stop()


if __name__ == "__main__":
    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        command = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "/help"
        print(handle_test(command))
        sys.exit(0)
    else:
        asyncio.run(main())