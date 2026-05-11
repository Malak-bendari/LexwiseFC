from dataclasses import dataclass


@dataclass
class User:
    id: int
    email: str
    name: str
    hashed_password: str
    subscription_level: str = "free"
