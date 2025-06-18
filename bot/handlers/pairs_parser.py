# bot/handlers/pairs_parser.py
from aiogram import Router, F
from parser.table_parser import extract_pairs
from core.db import upsert_pair

router = Router(name="pair_parser")

@router.message(F.text.contains("ZSCR"))
async def handle_zscr_table(msg):
    for a, b in extract_pairs(msg.text):
        await upsert_pair(a, b)
    await msg.answer("✅ Пари занесено до бази.")
