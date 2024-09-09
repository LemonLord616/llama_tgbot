from fastapi import FastAPI
from config import TELEGRAM_BOT_TOKEN, NGROK_TUNNEL_URL
from database import Db
from tgllm import Bot
from datetime import datetime
from logic import message_handler
import asyncio


app = FastAPI()
WEBHOOK_PATH = f"/bot/{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = f"{NGROK_TUNNEL_URL}{WEBHOOK_PATH}"


@app.on_event("startup")
async def on_startup():
    await Db().create_tables()

    webhook_info = await Bot().get("/getWebhookInfo")
    webhook_url = webhook_info["result"]["url"]
    if webhook_url != WEBHOOK_URL:
        await Bot().post("/setWebhook", {
            "url": WEBHOOK_URL,
        })


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    task = asyncio.create_task(message_handler(update))
