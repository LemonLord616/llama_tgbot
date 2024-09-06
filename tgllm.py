from fastapi import FastAPI


import aiohttp
import asyncio


from config import TELEGRAM_BOT_TOKEN

app = FastAPI()

def client_session_decorator(func):

    async def wrapper(*args, **kwargs):
        async with aiohttp.ClientSession() as session:
            response = await func(*args, **kwargs, session=session)
            if response.status != 200:
                raise Exception(f'Error: {response.status}')
            return await response.json()
    
    return wrapper


class LLM:
    url: str = 'http://10.100.30.243:1224'
    
    @client_session_decorator
    async def get_response(self, json_data, *_, session) -> str:
        return await session.post(self.url + "/v1/chat/completions", json=json_data)


class Bot:
    token: str = TELEGRAM_BOT_TOKEN
    url: str = 'https://api.telegram.org/bot'

    @client_session_decorator
    async def get(self, method, *_, session) -> str:
        return await session.get(self.url + self.token + method)
    
    @client_session_decorator
    async def post(self, method, json_data, *_, session) -> str:
        return await session.post(self.url + self.token + method, json=json_data)
