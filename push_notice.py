import asyncio
from datetime import datetime
from extraction import extract_and_update
from get_pdf import get_hrefs, get_pdf_file
import io
import mysql.connector
import os
import re
import telegram
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

load_dotenv()

mydb = mysql.connector.connect(
    host = os.getenv('MYSQL_HOST'),
    user = os.getenv('MYSQL_USER'),
    password = os.getenv('MYSQL_PASSWORD'),
    database = os.getenv('MYSQL_DATABASE'),
    port=os.getenv('MYSQL_PORT')
)

cursor = mydb.cursor()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

new_info = extract_and_update()
custom_messages = new_info["notices"]
n_files = new_info["n_files"]

# sending the pdf file to one user
async def send_pdf(bot, file, user_id):
    try:
        task = asyncio.create_task(bot.send_document(chat_id=user_id, document=file['pdf'], filename=file['filename']))
        print(f"PDF send to user {user_id}")
    except Exception as e:
        print(f"Failed to send PDF to user {user_id}: {e}")        
    await task

# sending pdf to all users
async def send_pdf_file(bot, file, user_ids):
    for user_id in user_ids:
        try:
            file['pdf'].seek(0)
            await send_pdf(bot, file, user_id)
        except Exception as e:
            print(e)

async def send_custom_message(bot, message, user_ids):
    tasks = {}
    for i, user_id in enumerate(user_ids):
        try:
            tasks[f'task{i}'] = asyncio.create_task(bot.send_message(chat_id=user_id, text=message))
            print(f"Message sent to user {user_id}")
        except Exception as e:
            print(f"Failed to send message to user {user_id}: {e}")
    for task in tasks:
        try:
            await tasks[task]
        except Exception as e:
            print(e)

async def main():
    trequest = HTTPXRequest(connection_pool_size=100000)
    bot = telegram.Bot(token=BOT_TOKEN, request=trequest)
    user_ids = []
    if custom_messages:
        cursor.execute("SELECT chat_id FROM chat_user")
        data = cursor.fetchall()
        user_ids = [i[0] for i in data]
        for message in custom_messages:
            await send_custom_message(bot, message='📜 ' + message, user_ids=user_ids)
        # sending pdfs
        hrefs = get_hrefs(top_n=n_files)
        pattern = r"^https://www\.imsnsit\.org/imsnsit/plum_url\.php"
        for href in hrefs:
            # CHECKING FOR VALID URLs
            if re.match(pattern, href):
                file = get_pdf_file(href)
                await send_pdf_file(bot, file, user_ids)
            else:
                await send_custom_message(bot, message=href, user_ids=user_ids)
        # await send_custom_message(bot, message='visit: https://www.imsnsit.org/imsnsit/notifications.php', user_ids=user_ids)
    

if __name__ == "__main__":
    with open('runs.txt', 'a') as file:
        file.write(str(datetime.now()) + ' This code was run \n')
    asyncio.run(main())
