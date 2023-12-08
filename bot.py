from telegram import *
from telegram.ext import *
import requests
import json
from types import SimpleNamespace
import math
import random
import time
from datetime import datetime
import pytz
from dateutil import tz

domain = "https://api.chootc.com"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Tham giá @chootcvn để mua, bán USDT số lượng lớn.",
        parse_mode=constants.ParseMode.HTML,
    )


async def messageHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    # print(chat_id)
    # await context.bot.send_message(
    #     chat_id, text="hello", parse_mode=constants.ParseMode.HTML
    # )


async def callback_minute(context: ContextTypes.DEFAULT_TYPE):

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    text = f"<b>1. Ví: {get_balance('TLd1GNEvc3f3av3Q6vPNS6KARbdA5ge5tQ')}</b> ____ \n"
    for index, item in enumerate(data):
        text += f"{index+2}. {item['name']}: {get_balance(item['wallet'])}\n"

    await context.bot.edit_message_text(
        chat_id="-1001986367510",
        message_id="26033",
        text=text,
        parse_mode=constants.ParseMode.HTML,
    )


def get_balance(address):
    url = "https://apilist.tronscan.org/api/account"
    payload = {
        "address": address,
    }
    res = requests.get(url, params=payload)
    trc20token_balances = json.loads(res.text)["trc20token_balances"]
    token_balance = next(
        (
            item
            for item in trc20token_balances
            if item["tokenId"] == "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        ),
        None,
    )
    if token_balance == None:
        return 0
    else:
        return f'{round(float(token_balance["balance"])*pow(10, -6)):,}'


app = (
    ApplicationBuilder().token("6979585989:AAG7G11LyxFo77KSGHUZxoc8XtZuaatO_c0").build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, messageHandler))

job_queue = app.job_queue

job_minute = job_queue.run_repeating(callback_minute, interval=60, first=10)

app.run_polling()
