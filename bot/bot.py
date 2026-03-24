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
        lab = parts[1] if len(parts) > 1 else "unknown"
        return handle_scores(lab)
    elif cmd == "/labs":
        return handle_labs()
    else:
        return handle_unknown(command)

async def main():
    from telegram.ext import ApplicationBuilder, CommandHandler
    from config import BOT_TOKEN

    async def start(update, context):
        await update.message.reply_text(handle_start())

    async def help_cmd(update, context):
        await update.message.reply_text(handle_help())

    async def health(update, context):
        await update.message.reply_text(handle_health())

    async def labs(update, context):
        await update.message.reply_text(handle_labs())

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("labs", labs))

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
