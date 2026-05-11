from dataclasses import dataclass


@dataclass
class AIProfile:
    id: int
    user_id: int
    preferences: dict
    alert_threshold: float = 0.0
    model_name: str = "default"
