import asyncpg
import os
import json
from utils.config import POSTGRESS_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
class PostgresDB:
    def __init__(self):
        self.host = POSTGRESS_HOST
        self.db = POSTGRES_DB
        self.user = POSTGRES_USER
        self.password = POSTGRES_PASSWORD
        self.conn = None

    async def connect(self):
        if not self.conn:
            self.conn = await asyncpg.connect(
                user=self.user,
                password=self.password,
                database=self.db,
                host=self.host
            )

    async def create_tables(self):
        await self.connect()
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT NOW()
        );
        """)

    async def save_message(self, session_id: str, role: str, message: str):
        await self.connect()
        await self.conn.execute("""
            INSERT INTO chat_logs (session_id, role, message)
            VALUES ($1, $2, $3);
        """, session_id, role, message)
