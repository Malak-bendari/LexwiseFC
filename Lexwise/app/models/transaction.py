from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    id: int
    user_id: int
    amount: float
    category: str
    date: datetime
    description: str = ""
