import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).with_suffix(".sqlite")

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS pairs (
    token_a      TEXT NOT NULL,
    token_b      TEXT NOT NULL,
    added_at     INTEGER,
    has_futures  INTEGER DEFAULT 0,
    PRIMARY KEY (token_a, token_b)
);
CREATE TABLE IF NOT EXISTS futures (
    exchange  TEXT NOT NULL,
    symbol    TEXT NOT NULL,      -- Напр. "BTCUSDT"
    PRIMARY KEY(exchange, symbol)
);

"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)

async def upsert_pair(token_a: str, token_b: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO pairs(token_a, token_b, added_at)
            VALUES (?, ?, strftime('%s','now'));
        """, (token_a, token_b))
        await db.commit()
