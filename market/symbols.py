# market/symbols.py
import asyncio, logging, httpx, time
from typing import List, Set, Dict

from core.config import EXCHANGES
from core.db import DB_PATH

import aiosqlite

log = logging.getLogger(__name__)

# ---------- helpers ---------------------------------------------------------

async def _get_binance_futures(client: httpx.AsyncClient) -> Set[str]:
    r = await client.get(EXCHANGES["binance"].futures_endpoint)
    r.raise_for_status()
    data = r.json()["symbols"]
    return {s["symbol"] for s in data if s["contractType"] == "PERPETUAL"}

async def _get_mexc_futures(client: httpx.AsyncClient) -> Set[str]:
    r = await client.get(EXCHANGES["mexc"].futures_endpoint)
    r.raise_for_status()
    data = r.json()["data"]
    return {item["symbol"] for item in data}

FETCHERS = {
    "binance": _get_binance_futures,
    "mexc": _get_mexc_futures,
}

# ---------- main updater ----------------------------------------------------

async def refresh_futures():
    """
    Завантажує списки ф’ючерс-символів для всіх EXCHANGES
    і оновлює таблиці `futures` та `pairs.has_futures`.
    """
    async with httpx.AsyncClient(timeout=20.0) as client, \
               aiosqlite.connect(DB_PATH) as db:

        all_tokens: Dict[str, Set[str]] = {}
        for name, fetch in FETCHERS.items():
            try:
                symbols = await fetch(client)
            except Exception as e:
                log.error("🔥  %s: %s", name, e)
                continue

            # зберегти до БД
            await db.execute("DELETE FROM futures WHERE exchange = ?", (name,))
            await db.executemany(
                "INSERT INTO futures(exchange, symbol) VALUES(?,?)",
                [(name, s) for s in symbols]
            )
            all_tokens[name] = {s[:-4] for s in symbols if s.endswith("USDT")}
            log.info("✓ %s futures loaded: %d symbols", name, len(symbols))

        # aggregate: токен має ф’ючерси хоч десь
        tokens_with_fut = set().union(*all_tokens.values())

        # оновити pairs.has_futures
        await db.execute("""
            UPDATE pairs
            SET has_futures = CASE
                WHEN token_a IN ({0}) AND token_b IN ({0}) THEN 1
                ELSE 0
            END
        """.format(",".join("?" * len(tokens_with_fut))), tuple(tokens_with_fut))
        await db.commit()

# ---------- CLI test --------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    asyncio.run(refresh_futures())
