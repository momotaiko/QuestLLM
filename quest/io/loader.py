import json
from typing import List
from quest.models import Quest

def load_quests(path: str) -> List[Quest]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Quest.from_dict(quest) for quest in data]

def save_quests(path: str, quests: List[Quest]):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([quest.to_dict() for quest in quests], f, ensure_ascii=False, indent=2)

