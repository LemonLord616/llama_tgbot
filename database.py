import sqlite3
import aiosqlite
from datetime import datetime
from typing import Callable
from config import DATABASE_NAME

CONTEXT_LIMIT = 10

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
                user_id INTEGER UNIQUE PRIMARY KEY,
                username TEXT
            );
            """)
        await connection.execute("""
            -- Создание таблицы dialogs
            CREATE TABLE IF NOT EXISTS dialogs (
                dialog_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER NOT NULL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
            """)
        await connection.execute("""
            -- Создание таблицы messages    
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                dialog_id INTEGER NOT NULL,
                role TEXT,
                content TEXT,
                time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dialog_id) REFERENCES dialogs(dialog_id)
            );
            """)
    
    @database_connection_decorator
    async def check_user(self, user_id, *_, connection,) -> bool:
        result = await connection.execute_fetchall(
            f"SELECT user_id FROM users WHERE user_id = {user_id};",
        )
        return bool(result)
    
    @database_connection_decorator
    async def check_dialog(self, user_id, *_, connection,) -> bool:
        result = await connection.execute_fetchall(
            f"SELECT dialog_id FROM dialogs WHERE user_id = {user_id};"
        )
        return bool(result)

    @database_connection_decorator
    async def get_last_dialog(self, user_id, *_, username=None, connection,) -> int:
        result = await connection.execute_fetchall(
            f"SELECT MAX(dialog_id) FROM dialogs WHERE user_id = {user_id};",
        )
        return result[0][0]
    

    @database_connection_decorator
    async def new_dialog(self, user_id, *_, username=None, connection,):
        await connection.execute(
            "INSERT OR IGNORE INTO users(user_id, username) VALUES(?, ?);",
            (user_id, username)
        )
        if await self.check_dialog(user_id):
            last_dialog: int = await self.get_last_dialog(user_id)
            await connection.execute(
                "UPDATE dialogs SET ended_at = ? WHERE dialog_id = ?;",
                (datetime.now(), last_dialog)
            )
        await connection.execute(
            "INSERT INTO dialogs(user_id) VALUES(?);",
            (user_id, )
        )

    @database_connection_decorator
    async def new_message(self, user_id, role, content, *_, username=None, connection,):

        if not await self.check_user(user_id) and not await self.check_dialog(user_id):
            await self.new_dialog(user_id, username=username)
        last_dialog: int = await self.get_last_dialog(user_id)
        print(last_dialog)
        await connection.execute(
            "INSERT INTO messages (dialog_id, role, content) VALUES (?, ?, ?)", (last_dialog, role, content)
        )
    
    @database_connection_decorator
    async def get_messages(self, user_id, *_, username=None, connection,):
        last_dialog: int = await self.get_last_dialog(user_id)
        messages_list: list = await connection.execute_fetchall(
            "SELECT * FROM messages WHERE dialog_id = ? ORDER BY message_id DESC LIMIT ?;",
            (last_dialog, CONTEXT_LIMIT)
        )
        messages = []
        for message in messages_list[::-1]:
            messages.append(
                {"role": message[2],
                "content": message[3],
                }
            )
        return messages
