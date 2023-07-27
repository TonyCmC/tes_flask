from flask import Blueprint
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

from config import *
from services.fugle_plotter_service import FuglePlotterService
from services.redis_service import RedisService
from utils.logger import Logger

logger = Logger('tgbot')
telegram_bot = Blueprint('telegram_bot', __name__)
application = ApplicationBuilder().token(TG_ACCESS_TOKEN).build()

fps = FuglePlotterService()
rds = RedisService()


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def update_tickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        df = fps.fetch_all_tickers()
        rds.update_tickers(df)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="股票對應表已更新完成")
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="[ERROR] 股票對應表更新錯誤\n" + e.args[0])
        logger.logger.error(e.args, exc_info=True)


async def get_minute_plot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        pass
    except ValueError as ve:
        logger.logger.error(ve.args, exc_info=True)
    except Exception as e:
        logger.logger.error(e.args, exc_info=True)


echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
application.add_handler(echo_handler)
application.add_handler(CommandHandler('update_list', update_tickers))
application.run_polling()
