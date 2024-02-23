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
    
    if "/update" in update.message.text:
        res = requests.get("https://api.chootc.com/api/tracking")
        wallets = res.json()
        data = []
        for item in wallets:
            if item["note"] == 2:
                data.append(
                {
                    "name": item["name"],
                    "wallet": item["address"],
                    "block_timestamp": 1706281575000,
                }
            )

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


async def callback_minute(context: ContextTypes.DEFAULT_TYPE):

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    text = f"<b>1. Ví: {get_balance('TLd1GNEvc3f3av3Q6vPNS6KARbdA5ge5tQ')}</b> ____ \n"
    for index, item in enumerate(data):
        text += f"{index+2}. {item['name']}: {get_balance(item['wallet'])}\n"

    buy = requests.get(f"{domain}/api/p2p?type=buy&asset=usdt&fiat=vnd&page=1")
    sell = requests.get(f"{domain}/api/p2p?type=sell&asset=usdt&fiat=vnd&page=1")

    buy_price = buy.json()["data"][19]["adv"]["price"]
    sell_price = sell.json()["data"][19]["adv"]["price"]
 
    text += f"\n<b>{int(buy_price):,} | {int(sell_price):,} | {int((int(buy_price) + int(sell_price))/2):,}</b>"

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

job_minute = job_queue.run_repeating(callback_minute, interval=90, first=10)

app.run_polling()
