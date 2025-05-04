from quest.models import *
from quest.processing.first_quest_llm import first_questLLM
from quest.processing.second_quest_llm import second_questLLM
from quest.processing.contextual_retrieve import contextual_search
from quest.processing.keyword_retrieve import keyword_search
from quest.processing.update import status_update
from quest.io.loader import load_quests
from config.environment import QUEST_JSON_PATH

def questLLM(game_status: GameStatus,
             quest_status: QuestStatus,
             conversation_history: List[Dict]):
    '''

    현재는 퀘스트들이 samples.py, quest.json에서 로드됨. 
    추후에 본 서버와 코드 합칠때 quests는 quest_status의 정보만으로 재구성될 수 있도록 설계해야 함.

    설계 방향성:

    - 각 퀘스트들의 정의는 Session independent하므로 서버 내에 JSON으로 저장

    - 각 퀘스트들이 만족되었는지(quest_status.quest_completion_status)와 
    각 퀘스트에 해당하는 로어가 프롬프트에 몇 턴간 포함될지(quest_status.quest_remaining_turns)는 
    Session dependent하므로, QuestStatus의 형태로 외부로부터 전달받음

    '''

    # load quests
    quests = load_quests(QUEST_JSON_PATH)
    
    # 1stQuestLLM
    extracted_sentence, extracted_keywords = first_questLLM(conversation_history)

    # Retrieve (현재 게임 상태 조건에 맞는 퀘스트만 retrieve)
    # 의미 기반 퀘스트 검색
    context_based_retrieved_quest_ids = contextual_search(quests, extracted_sentence, game_status, quest_status, top_k=2)
    # 단어 기반 퀘스트 검색
    keyword_based_retrieved_quest_ids = keyword_search(quests, extracted_keywords, game_status, quest_status)

    # 2ndQuestLLM
    quest_check_results = second_questLLM(quests, 
                                          context_based_retrieved_quest_ids, 
                                          keyword_based_retrieved_quest_ids, 
                                          extracted_sentence, extracted_keywords, 
                                          conversation_history)
    
    # -------- 작동 확인용 로그 ------------
    print(f"latest user message: {conversation_history[-2]['content']}")
    print(f"extracted_sentence: {extracted_sentence}")
    print(f"extracted_keywords: {extracted_keywords}")
    print("")

    print(f"의미 기반 퀘스트 검색 결과: {[quests[i].title for i in context_based_retrieved_quest_ids]}")
    print(f"키워드 기반 퀘스트 검색 결과: {[quests[i].title for i in keyword_based_retrieved_quest_ids]}")
    print("")
    print("퀘스트 검사 결과: ")
    for qid, result in quest_check_results.items():
        print(f"{quests[qid].title}: {result}")
    print("")
    # -----------------------------------

    # status update 
    next_game_status, next_quest_status = status_update(game_status, quest_status, quests, quest_check_results)

    return next_game_status, next_quest_status
