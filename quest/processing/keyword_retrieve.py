from typing import List
from quest.models import *

def keyword_search(quests: List[Quest],
                   extracted_keywords: List[str], 
                   game_status: GameStatus,
                   quest_status: QuestStatus) -> List[int]:
    
    query_keyword_set = set(extracted_keywords)

    retrieved_quest_ids = []
    for quest in quests:
        skip_evaluation = (
            quest.status == QuestCompletionStatus.REPEATABLE
            and quest.type in {QuestType.LIKEABILITY, QuestType.PERSUASION}
        )

        if skip_evaluation:
            continue
        
        activation = is_quest_activated(quest, game_status, quest_status)
        if not activation:
            continue

        if quest.trigger.keyword_trigger and quest.trigger.keyword_trigger.keywords:
            quest_keywords = quest.trigger.keyword_trigger.keywords
            if query_keyword_set & set(quest_keywords): 
                retrieved_quest_ids.append(quest.id)

    return retrieved_quest_ids

def is_quest_activated(quest: Quest, 
                       game_status: GameStatus, 
                       quest_status: QuestStatus) -> bool:
    
    # game_status 검사
    quest_activation_conditions = quest.activation_conditions
    if quest_activation_conditions.likeability_min > game_status.likeability:
        return False 
    if quest_activation_conditions.persuasion_min > game_status.persuasion:
        return False
    
    # quest_status 검사 
    dependencies = quest.dependencies
    for quest_id in dependencies:
        if quest_status.quest_completion_status[quest_id] == QuestCompletionStatus.NOT_COMPLETED:
                return False
            
    return True






    