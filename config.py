TELEGRAM_BOT_TOKEN = "7528442945:AAGthgzCkx0F_lu_4MX1248Ol8VEKdtvw5k"
NGROK_TUNNEL_URL = "https://4de8-188-130-155-168.ngrok-free.app"
DATABASE_NAME = "abobus228.db"

SYSTEM_PROMPT = "Тебя зовут Абоба228. Ты молодёжный и крутой"
#SYSTEM_PROMPT = "Ты ассистент по имени Абоба. Абоба очень часто вставляет в свою речь слова 'блять', 'пиздец', 'ёпта', 'нахуй' и иные производные от этих слов. Это такая привычка. Также он очень молодежный и крутой"
CONTEXT_LIMIT = 10
TIME_BETWEEN_REQUESTS = 3

MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"

JSON_PARAMETERS = {
    "n": 1,
    "model": MODEL_NAME,
    "stream": True,
    "stream_options": {
        "include_usage": False,
        "continuous_usage_stats": False
    }
}

GROUPCHAT_MAXTOKEN = 128
USERCHAT_MAXTOKEN = 10000