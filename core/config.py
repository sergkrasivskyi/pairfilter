# core/config.py
from pydantic import BaseModel
from typing import Dict

class Exchange(BaseModel):
    name: str
    rest_url: str
    futures_endpoint: str     # относительный шлях
    ws_url: str

EXCHANGES: Dict[str, Exchange] = {
    "binance": Exchange(
        name="Binance",
        rest_url="https://fapi.binance.com",
        futures_endpoint="/fapi/v1/exchangeInfo",
        ws_url="wss://stream.binance.com/stream"
    ),
    "mexc": Exchange(
        name="MEXC",
        rest_url="https://contract.mexc.com",
        futures_endpoint="/api/v1/contract/detail",
        ws_url="wss://contract.mexc.com/ws"
    ),
}
