from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict

class QuestType(Enum):
    STORY = "STORY"
    LIKEABILITY = "LIKEABILITY"
    PERSUASION = "PERSUASION"
    TALKPOINT = "TALKPOINT"
    LOREBOOK = "LOREBOOK"

class QuestCompletionStatus(Enum):
    REPEATABLE = "REPEATABLE"
    NOT_COMPLETED = "NOT_COMPLETED"
    COMPLETED = "COMPLETED"

@dataclass
class GameStatus:
    likeability: float = 0
    persuasion: float = 0

@dataclass
class QuestStatus:
    quest_completion_status: Dict[int, QuestCompletionStatus] = field(default_factory=dict) 
    quest_remaining_turns: Dict[int, int] = field(default_factory=dict)
    

@dataclass
class SemanticTrigger:
    semantics: Optional[List[str]] = None # e.g. 미케에게 공감해주는 대화인가?
    embeddings: Optional[List[List[float]]] = None

    @staticmethod
    def from_dict(data: dict) -> "SemanticTrigger":
        return SemanticTrigger(**data)
    
    def to_dict(self) -> dict:
        return {
            "semantics": self.semantics,
            "embeddings": self.embeddings
        }

@dataclass
class KeywordTrigger:
    keywords: Optional[List[str]] = None # e.g. 아버지, 추투라
    embeddings: Optional[List[float]] = None

    @staticmethod
    def from_dict(data: dict) -> "KeywordTrigger":
        return KeywordTrigger(**data)
    
    def to_dict(self) -> dict:
        return {
            "keywords": self.keywords,
            "embeddings": self.embeddings
        }

@dataclass
class Trigger:
    semantic_trigger: Optional[SemanticTrigger] = None
    keyword_trigger: Optional[KeywordTrigger] = None

    @staticmethod
    def from_dict(data: dict) -> "Trigger":
        return Trigger(
            semantic_trigger=SemanticTrigger.from_dict(data["semantic_trigger"]) if data.get("semantic_trigger") else None,
            keyword_trigger=KeywordTrigger.from_dict(data["keyword_trigger"]) if data.get("keyword_trigger") else None
        )
    
    def to_dict(self) -> dict:
        return {
            "semantic_trigger": self.semantic_trigger.to_dict() if self.semantic_trigger else None,
            "keyword_trigger": self.keyword_trigger.to_dict() if self.keyword_trigger else None
        }

@dataclass
class ActivationConditions:
    likeability_min: int = 0
    persuasion_min: int = 0

    @staticmethod
    def from_dict(data: dict) -> "ActivationConditions":
        return ActivationConditions(**data)
    
    def to_dict(self) -> dict:
        return {
            "likeability_min": self.likeability_min,
            "persuasion_min": self.persuasion_min
        }

@dataclass
class CompletionCriteria:
    output_format: List[str] = field(default_factory=lambda: ["yes", "no"])
    last_result: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "CompletionCriteria":
        return CompletionCriteria(**data)
    
    def to_dict(self) -> dict:
        return {
            "output_format": self.output_format,
            "last_result": self.last_result
        }

@dataclass
class Quest:
    id: int
    type: QuestType
    title: str
    query_for_llm: str

    description_for_prompt: str = field(default_factory=str)
    remaining_turns: int = 0
    dependencies: List[int] = field(default_factory=list)
    activation_conditions: ActivationConditions = field(default_factory=ActivationConditions)
    trigger: Trigger = field(default_factory=Trigger)
    status: QuestCompletionStatus = QuestCompletionStatus.NOT_COMPLETED
    completion_criteria: CompletionCriteria = field(default_factory=CompletionCriteria)

    @staticmethod
    def from_dict(data: dict) -> "Quest":
        return Quest(
            id=data["id"],
            type=QuestType(data["type"]),
            title=data["title"],
            query_for_llm=data["query_for_llm"],

            description_for_prompt=data["description_for_prompt"],
            remaining_turns=data["remaining_turns"],
            dependencies=data.get("dependencies", []),
            activation_conditions=ActivationConditions.from_dict(data["activation_conditions"]),
            trigger=Trigger.from_dict(data["trigger"]),
            status=QuestCompletionStatus(data["status"]),
            completion_criteria=CompletionCriteria.from_dict(data["completion_criteria"])
        )
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "query_for_llm": self.query_for_llm,

            "description_for_prompt": self.description_for_prompt,
            "remaining_turns": self.remaining_turns,
            "dependencies": self.dependencies,
            "activation_conditions": self.activation_conditions.to_dict(),
            "trigger": self.trigger.to_dict(),
            "status": self.status.value,
            "completion_criteria": self.completion_criteria.to_dict(),
        }