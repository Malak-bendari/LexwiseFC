from dataclasses import dataclass


@dataclass
class Budget:
    id: int
    user_id: int
    category: str
    amount: float
    period: str
