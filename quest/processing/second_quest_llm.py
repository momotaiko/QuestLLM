import json
import json5
import openai
from typing import List, Dict
from quest.models import *
from quest.prompt import *
from config.environment import API_KEY, SECOND_CHAT_MODEL

try:
    client = openai.OpenAI(api_key=API_KEY)
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    exit()

# 반환 형태: {<quest_id>: "criterion", ...} (e.g. {0: "yes", 3: "no", 4: "medium", ...})
def second_questLLM(quests: List[Quest],
                    context_based_retrieved_quest_ids: List[int], 
                    keyword_based_retrieved_quest_ids: List[int], 
                    extracted_sentence: str,
                    extracted_keywords: List[str],
                    conversation_history: List[Dict]) -> Dict[int, str]:
    
    conversation_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" \
                                for msg in conversation_history if msg['role'] != 'system'])
    
    # 의미 검색, 단어 검색 둘 다에 걸린 퀘스트가 있으면 keyword based retrieved로 간주
    # 필수 체크가 필요한 REPEATABLE 퀘스트들은 context based retrieved로 간주
    keyword_set = set(keyword_based_retrieved_quest_ids)
    context_based_retrieved_quest_ids = [quest_id for quest_id in context_based_retrieved_quest_ids \
                                         if quest_id not in keyword_set]
    
    requires_mandatory_check_quest_ids = []
    for quest in quests:
        is_mandatory = (
            quest.status == QuestCompletionStatus.REPEATABLE
            and quest.type in {QuestType.LIKEABILITY, QuestType.PERSUASION}
        )
        if is_mandatory:
            requires_mandatory_check_quest_ids.append(quest.id)

    context_based_retrieved_quest_ids = context_based_retrieved_quest_ids + requires_mandatory_check_quest_ids

    # quests의 idx가 곧 quest_id
    # 예시: prompt.py line 130
    context_based_retrieved_quest_dict = {}
    for offset, quest_id in enumerate(context_based_retrieved_quest_ids):
        key = f"{offset+1}. {quests[quest_id].query_for_llm}"
        context_based_retrieved_quest_dict[key] = quests[quest_id].completion_criteria.to_dict()
        
    context_str = json.dumps(context_based_retrieved_quest_dict, ensure_ascii=False, indent=4)
        
    keyword_based_retrieved_quest_dict = {}
    for offset, quest_id in enumerate(keyword_based_retrieved_quest_ids):
        key = f"{len(context_based_retrieved_quest_ids) + offset + 1}. {quests[quest_id].query_for_llm}"
        keyword_based_retrieved_quest_dict[key] = quests[quest_id].completion_criteria.to_dict()

    keyword_str = json.dumps(keyword_based_retrieved_quest_dict, ensure_ascii=False, indent=4)

    try:
        second_questLLM_prompt_content = second_QuestLLM_system_prompt.format(
            conversation_history=conversation_str,
            extracted_sentence=extracted_sentence,
            extracted_keywords=extracted_keywords,
            context_based_retrieved_quests=context_str,
            keyword_based_retrieved_quests=keyword_str
        )
    except KeyError as e:
        print(f"Error formatting second_QuestLLM_system_prompt: Missing key {e}") 
        second_questLLM_prompt_content = "Error: Prompt formatting failed."

    second_llm_messages = [{"role": "system", "content": second_questLLM_prompt_content}]

    if "Error:" not in second_questLLM_prompt_content:
        second_questLLM_output = get_openai_chat_completion(second_llm_messages, model=SECOND_CHAT_MODEL)
    else:
        print("Some error occured in 'first_questLLM_prompt_content'")
        return {}
    
    total_retrieved_quest_ids = context_based_retrieved_quest_ids + keyword_based_retrieved_quest_ids
    quest_check_results = process_second_questLLM_output(second_questLLM_output, total_retrieved_quest_ids)
    return quest_check_results

def get_openai_chat_completion(messages: list, model: str = SECOND_CHAT_MODEL, temperature: float = 0.7) -> str:
    """Gets a chat completion response from OpenAI API."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting chat completion: {e}")
        print(f"Messages sent: {messages}") # Log messages for debugging
        return f"Error: Could not get response from {model}." # Return error message
    
def process_second_questLLM_output(output: str, total_retrieved_quest_ids: List[int]) -> Dict[int, str]:
    try:
        data = json5.loads(output)
        checked_quest_list = data.get("context_based_retrieved_quests", []) + data.get("keyword_based_retrieved_quests", [])

        quest_check_results = {}
        for i in range(len(checked_quest_list)):
            entry = checked_quest_list[i]
            idx = entry["quest_idx"] - 1
            quest_id = total_retrieved_quest_ids[idx]
            quest_check_results[quest_id] = entry["result"]

        return quest_check_results

    except json5.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        return {}

