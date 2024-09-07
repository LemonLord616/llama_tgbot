import aiohttp
import asyncio
import json

from config import TELEGRAM_BOT_TOKEN


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
    
    async def get_response(self, json_data):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url + "/v1/chat/completions", json=json_data) as response:
                if response.status != 200:
                    raise Exception(f"Error: {response.status}")
                async for line in response.content.iter_chunks():
                    try:
                        chunk = json.loads(line[0][6:-2])
                        yield chunk["choices"][0]["delta"]["content"]
                    except:
                        pass


class Bot:
    token: str = TELEGRAM_BOT_TOKEN
    url: str = 'https://api.telegram.org/bot'

    @client_session_decorator
    async def get(self, method, *_, session) -> str:
        return await session.get(self.url + self.token + method)
    
    @client_session_decorator
    async def post(self, method, json_data, *_, session) -> str:
        return await session.post(self.url + self.token + method, json=json_data)
