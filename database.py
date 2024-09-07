import sqlite3
import aiosqlite
from datetime import datetime
from typing import Callable
from config import DATABASE_NAME, CONTEXT_LIMIT


def database_connection_decorator(func):

    async def wrapper(*args, **kwargs):
        async with aiosqlite.connect(DATABASE_NAME) as connection:
            response = await func(*args, **kwargs, connection=connection)
            await connection.commit()
            return response
    
    return wrapper

def is_empty(lst: list):
    return not lst


class Db():
    
    @database_connection_decorator
    async def create_tables(self, *_, connection,):
        await connection.execute("""
            -- Создание таблицы users
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER UNIQUE PRIMARY KEY,
                username TEXT
            );
            """)
        await connection.execute("""
            -- Создание таблицы dialogs
            CREATE TABLE IF NOT EXISTS dialogs (
                dialog_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                chat_id INTEGER NOT NULL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            );
            """)
        await connection.execute("""
            -- Создание таблицы messages    
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                dialog_id INTEGER NOT NULL,
                username TEXT,
                role TEXT,
                content TEXT,
                time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dialog_id) REFERENCES dialogs(dialog_id)
            );
            """)
    
    @database_connection_decorator
    async def check_user(self, chat_id, *_, connection,) -> bool:
        result = await connection.execute_fetchall(
            f"SELECT chat_id FROM users WHERE chat_id = {chat_id};",
        )
        return bool(result)
    
    @database_connection_decorator
    async def check_dialog(self, chat_id, *_, connection,) -> bool:
        result = await connection.execute_fetchall(
            f"SELECT dialog_id FROM dialogs WHERE chat_id = {chat_id};"
        )
        return bool(result)

    @database_connection_decorator
    async def get_last_dialog(self, chat_id, *_, username="NULL", connection,) -> int:
        result = await connection.execute_fetchall(
            f"SELECT MAX(dialog_id) FROM dialogs WHERE chat_id = {chat_id};",
        )
        return result[0][0]
    

    @database_connection_decorator
    async def new_dialog(self, chat_id, *_, username="NULL", connection,):
        
        await connection.execute(
            "INSERT OR IGNORE INTO users(chat_id, username) VALUES(?, ?);",
            (chat_id, username)
        )
        if await self.check_dialog(chat_id):
            last_dialog: int = await self.get_last_dialog(chat_id)
            await connection.execute(
                "UPDATE dialogs SET ended_at = ? WHERE dialog_id = ?;",
                (datetime.now(), last_dialog)
            )
        await connection.execute(
            "INSERT INTO dialogs(chat_id) VALUES(?);",
            (chat_id, )
        )

    @database_connection_decorator
    async def new_message(self, chat_id, role, content, *_, username="NULL", connection,):

        if not await self.check_user(chat_id) and not await self.check_dialog(chat_id):
            await self.new_dialog(chat_id, username=username)
        last_dialog: int = await self.get_last_dialog(chat_id)
        await connection.execute(
            "INSERT INTO messages (dialog_id, username, role, content) VALUES (?, ?, ?, ?)", (last_dialog, username, role, content)
        )
    
    @database_connection_decorator
    async def get_messages(self, chat_id, *_, connection,):
        last_dialog: int = await self.get_last_dialog(chat_id)
        messages_list: list = await connection.execute_fetchall(
            "SELECT * FROM messages WHERE dialog_id = ? ORDER BY message_id DESC LIMIT ?;",
            (last_dialog, CONTEXT_LIMIT)
        )
        messages = []
        for message in messages_list[::-1]:
            messages.append({
                "name": message[2],
                "role": message[3],
                "content": message[4]
                }
            )
        return messages
