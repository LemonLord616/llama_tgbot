from tgllm import LLM, Bot
from database import Db
from config import SYSTEM_PROMPT, JSON_PARAMETERS, TIME_BETWEEN_REQUESTS, MODEL_NAME

import asyncio
from datetime import datetime

LAST_REQUEST_TIME = datetime.now()


def update_analyze(update: dict) -> dict:
    try:
        username = update["message"]["from"]["username"]
    except:
        username = "NULL"
    try:
        message = {
            "message_id": update["message"]["message_id"],
            "chat_id": update["message"]["chat"]["id"],
            "role": "assistant" if update["message"]["from"]["is_bot"] else "user",
            "content": update["message"]["text"],
            "username": username,
        }
        return message
    except:
        return False


async def request_wait():
    global LAST_REQUEST_TIME
    seconds = (datetime.now() - LAST_REQUEST_TIME).total_seconds()
    while seconds < TIME_BETWEEN_REQUESTS:
        await asyncio.sleep(TIME_BETWEEN_REQUESTS - seconds)
        seconds = (datetime.now() - LAST_REQUEST_TIME).total_seconds()
    LAST_REQUEST_TIME = datetime.now()


async def message_logic(update):
    message = update_analyze(update)
    if not message:
        return
    bot_message = {}

    text_inmessage = "*Абоба думает...*"
    text_overall = ""
    text_troetochie = "..."

    if not message:
        return
    if message["role"] == "user" and message["content"] in ["/start", "/clear_context"]:
        await Db().new_dialog(message["chat_id"], username=message["username"])
        return
    await Db().new_message(message["chat_id"], message["role"], message["content"], username=message["username"])

    async def send_message():

        try:
            bot_message = await Bot().post("/sendMessage",{
                "chat_id": message["chat_id"],
                "text": text_inmessage,
                "n": 1,
                "parse_mode": "Markdown",
                "reply_parameters":{
                    "message_id": message["message_id"],
                }
            })
            await Bot().post("/sendChatAction", {
                "chat_id": bot_message["result"]["chat"]["id"],
                "action": "typing"
                }
            )
            return bot_message

        except Exception as e:
            print(e)
            return {}
    
    async def update_message():
        try:
            await Bot().post("/editMessageText", {
                "chat_id": bot_message["result"]["chat"]["id"],
                "message_id": bot_message["result"]["message_id"],
                "text": text_inmessage + text_troetochie if text_inmessage else "Что-то пошло не так..."
            })
            await Bot().post("/sendChatAction", {
                "chat_id": bot_message["result"]["chat"]["id"],
                "action": "typing"
                }
            )
        except Exception as e:
            print(e)

    if message["role"] == "user":
        messages = await Db().get_messages(message["chat_id"])
        messages = [{
            "role": "system",
            "content": SYSTEM_PROMPT
            }
        ] + messages

        
        await request_wait()
        bot_message = await send_message()

        json_data = JSON_PARAMETERS
        json_data["messages"] = messages

        if message["chat_id"] < 0:
            json_data["max_tokens"] = 128

        text_inmessage = ""


        async for chunk in LLM().get_response(json_data):

            text_overall += chunk
            text_inmessage += chunk
            if (datetime.now() - LAST_REQUEST_TIME).total_seconds() >= TIME_BETWEEN_REQUESTS:

                slice_index = 4096 - len(text_troetochie)

                if len(text_inmessage) > slice_index:
                    text_inmessage = chunk
                    temp = text_inmessage[slice_index:]
                    text_inmessage = text_inmessage[:slice_index]

                    while text_inmessage:
                        await request_wait()
                        bot_message = await send_message()

                        if not temp:
                            break

                        text_inmessage = temp
                        temp = text_inmessage[slice_index:]
                        text_inmessage = text_inmessage[:slice_index]
                
                else:
                    await request_wait()
                    await update_message()
        
        text_troetochie = ""
        await request_wait()
        await update_message()

        await Db().new_message(message["chat_id"], "assistant", text_overall, username=MODEL_NAME)
