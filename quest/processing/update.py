from typing import List, Dict, Tuple
from quest.models import *
from config.environment import LORE_REMAINING_DURATION

def status_update(game_status: GameStatus,
                  quest_status: List[Quest],
                  quests: List[Quest], 
                  quest_check_results: Dict[int, str]) -> Tuple[GameStatus, QuestStatus]:
    
    delta_likeability = 0; delta_persuasion = 0
    lore_just_activated = set()

    for quest_id, criterion in quest_check_results.items():
        quest = quests[quest_id]
        criterion = criterion.lower()
        criteria = [c.lower() for c in quest.completion_criteria.output_format]

        # GameStatus 새로 계산
        if quest.type == QuestType.LIKEABILITY:
            if criterion in criteria:
                delta_likeability += (criteria.index(criterion) + 1) / len(criteria)
            else:
                print(f"Error: {quest.title}: {criterion} is not in {criteria}")

            # Likeability를 올리는 기존의 REPEATABLE한 이벤트가 아닌 다른 단발성 이벤트가 존재할 경우
            # 해당 단발성 이벤트가 delta_likeability에 끼치는 영향은 추후에 고려
            if quest.status == QuestCompletionStatus.NOT_COMPLETED:
                quest.status = QuestCompletionStatus.COMPLETED

        elif quest.type == QuestType.PERSUASION:
            if criterion in criteria:
                delta_persuasion += (criteria.index(criterion) + 1) / len(criteria)
            else:
                print(f"Error: {quest.title}: {criterion} is not in {criteria}")

            if quest.status == QuestCompletionStatus.NOT_COMPLETED:
                quest.status = QuestCompletionStatus.COMPLETED

        # QuestStatus 새로 계산
        # LIKEABILITY, PERSUASION 타입이 아닌 퀘스트들은 completion_criteria를 ["yes", "no"] 로 고정시켰다고 가정
        # 현재 LORE_REMAINING_DURATION = 3
        else:
            if criterion == "yes":
                quest.status = QuestCompletionStatus.COMPLETED
                lore_just_activated.add(quest_id)
       
    new_likeability = game_status.likeability + delta_likeability
    new_persuasion = game_status.persuasion + delta_persuasion
    next_game_status = GameStatus(likeability=new_likeability, persuasion=new_persuasion)

    new_quest_completion_status = {quest.id: quest.status for quest in quests}
    new_quest_remaining_turns = {}
    for quest in quests:
        current = quest_status.quest_remaining_turns[quest.id]
        if current is None:
            new_quest_remaining_turns[quest.id] = None
        elif quest.id in lore_just_activated:
            new_quest_remaining_turns[quest.id] = LORE_REMAINING_DURATION
        elif current > 0:
            new_quest_remaining_turns[quest.id] = current - 1
        else:
            new_quest_remaining_turns[quest.id] = 0

    next_quest_status = QuestStatus(quest_completion_status=new_quest_completion_status, 
                                    quest_remaining_turns=new_quest_remaining_turns)
    
    return next_game_status, next_quest_status


    