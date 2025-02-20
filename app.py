from extraction import get_new_state, get_new_soup
from push_notice import send_custom_message
import os
import telegram
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import mysql.connector


TOKEN: Final = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME: Final = '@NSUTNotificationsBot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mydb = mysql.connector.connect(
    host = os.getenv('MYSQLHOST'),
    user = os.getenv('MYSQLUSER'),
    password = os.getenv('MYSQLPASSWORD'),
    database = os.getenv('MYSQLDATABASE'),
    port=os.getenv('MYSQLPORT')
    )
    cursor = mydb.cursor()
    user_ids = []
    current_id = update.message.chat_id
    print(current_id)

    cursor.execute("SELECT chat_id FROM users")
    data = cursor.fetchall()
    user_ids = [int(i[0]) for i in data]

    if current_id not in user_ids:
        cursor.execute("INSERT INTO users (chat_id) VALUES (%s)", (current_id, ))
        mydb.commit()
        print("user added")
    await update.message.reply_text("Hi😇 You'll recieve new notices when they arrive. Below are some recent notices...")
    trequest = HTTPXRequest(connection_pool_size=1000)
    bot = telegram.Bot(token=TOKEN, request=trequest)
    new_soup = get_new_soup()
    for notice in get_new_state()[:5]:
        await send_custom_message(bot, message='📜 '+ notice, user_ids=[current_id])
    await send_custom_message(bot, message='visit: https://www.imsnsit.org/imsnsit/notifications.php', user_ids=[current_id])


if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))

    # Polls the bot
    print("polling...")
    app.run_polling(poll_interval=3)