# parser/table_parser.py
import re
from typing import Iterable, Tuple

PAIR_RE = re.compile(r"\d+\.\d+\s+\|\s+\d+\.\d+\s+\|\s+([A-Z]{2,10})/([A-Z]{2,10})")

def extract_pairs(text: str) -> Iterable[Tuple[str, str]]:
    """
    Витягає ('TOKENA', 'TOKENB') із Telegram-повідомлення таблиці.
    Ігнорує ZSCR та COR.
    """
    for m in PAIR_RE.finditer(text):
        yield m.group(1), m.group(2)
