from fastapi import FastAPI
from tgllm import Bot, LLM
from config import TELEGRAM_BOT_TOKEN, NGROK_TUNNEL_URL, SYSTEM_PROMPT
from database import Db


app = FastAPI()
WEBHOOK_PATH = f"/bot/{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = f"{NGROK_TUNNEL_URL}{WEBHOOK_PATH}"

def update_analyze(update: dict) -> dict:
    try:
        message = {
            "user_id": update["message"]["chat"]["id"],
            "role": "assistant" if update["message"]["from"]["is_bot"] else "user",
            "content": update["message"]["text"],
            "username": update["message"]["from"]["username"],
        }
        return message
    except:
        return False

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
    print(update)
    message = update_analyze(update)
    print(message)
    if not message:
        return
    if message["role"] == "user" and message["content"] in ["/start", "/clear_context"]:
        await Db().new_dialog(message["user_id"], username=message["username"])
        return
    await Db().new_message(message["user_id"], message["role"], message["content"], username=message["username"])

    if message["role"] == "user":
        messages = await Db().get_messages(message["user_id"], username=message["username"])
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

        print(messages)
        response = await LLM().get_response({
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "messages": messages
        })
        print(response)
        await Bot().post("/sendMessage",{
            "chat_id": message["user_id"],
            "text": response["choices"][0]["message"]["content"],
            "n": 1,
        })
