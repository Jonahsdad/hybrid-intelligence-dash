# pages/_registry.py
from dataclasses import dataclass

@dataclass
class Arena:
    key: str   # label in dropdown
    module: str  # python module path under pages/

ARENAS = [
    Arena(key="crypto flagship", module="pages.crypto_flagship"),
]
