from quest.engine import questLLM
from quest.io.loader import save_quests
from sample.samples import *
from config.environment import CONVERSATION_SAMPLE_PATH, QUEST_JSON_PATH

def load_json_sample(path):
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":

    # 샘플 로드
    conversation_history = load_json_sample(CONVERSATION_SAMPLE_PATH)
    sample_quest_list = quest_initialization()
    save_quests(QUEST_JSON_PATH, sample_quest_list)

    # 메인 로직
    next_game_status, next_quest_status = questLLM(game_status, quest_status, conversation_history)

    # -------- 작동 확인용 로그 ------------
    print(f"이전 likeability: {game_status.likeability:.2f}, 이전 persuasion: {game_status.persuasion:.2f}")

    print(f"이전 퀘스트 달성 상태: ")
    for quest_id, status in quest_status.quest_completion_status.items():
        print(f"\t퀘스트 {quest_id}: {status.value}")

    print(f"이전 각 로어의 활성화 수명: ")
    for quest_id, turns in quest_status.quest_remaining_turns.items():
        print(f"\t퀘스트 {quest_id}: {turns}턴 남음") 

    print("\n")

    print(f"다음 likeability: {next_game_status.likeability:.2f}, 다음 persuasion: {next_game_status.persuasion:.2f}")

    print("갱신된 퀘스트 달성 상태:")
    for quest_id, status in next_quest_status.quest_completion_status.items():
        print(f"\t퀘스트 {quest_id}: {status.value}")

    print("갱신된 각 로어의 활성화 수명:")
    for quest_id, turns in next_quest_status.quest_remaining_turns.items():
        print(f"\t퀘스트 {quest_id}: {turns}턴 남음")
    # -------------------------------------
