from dataclasses import dataclass
from typing import Optional

@dataclass
class FAQ:
    id: Optional[int]
    question: str
    answer: str
    category: str
    created_date: str
    updated_date: str
    usage_count: int = 0
    is_favorite: bool = False

@dataclass
class HistoryRecord:
    id: Optional[int]
    user_question: str
    bot_answer: str
    confidence_score: float
    timestamp: str
    response_time_ms: float
    category: str

@dataclass
class AppSetting:
    key: str
    value: str
