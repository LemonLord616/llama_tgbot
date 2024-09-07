TELEGRAM_BOT_TOKEN = "7528442945:AAGthgzCkx0F_lu_4MX1248Ol8VEKdtvw5k"
NGROK_TUNNEL_URL = "https://e2aa-85-249-29-214.ngrok-free.app"
DATABASE_NAME = "abobus228.db"

SYSTEM_PROMPT = "Тебя зовут Абоба228. Ты очень молодёжный и крутой"
CONTEXT_LIMIT = 10
TIME_BETWEEN_REQUESTS = 3

MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"

JSON_PARAMETERS = {
    "n": 1,
    "model": MODEL_NAME,
    "max_tokens": 10000,
    "stream": True,
    "stream_options": {
        "include_usage": False,
        "continuous_usage_stats": False
    }
}