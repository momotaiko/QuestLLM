from typing import List, Dict, Tuple
from quest.prompt import *
import openai
import json5 # json 파싱 
from config.environment import API_KEY, FIRST_CHAT_MODEL

try:
    client = openai.OpenAI(api_key=API_KEY)
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    exit()

# 대화 기록을 받아서 extracted_sentence, extracted_keywords를 반환
def first_questLLM(conversation_history: Dict) -> Tuple[str, List[str]]:
    conversation_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" \
                                  for msg in conversation_history if msg['role'] != 'system'])
    
    try: 
        first_questLLM_prompt_content = first_QuestLLM_system_prompt.format(
            conversation_history=conversation_str,
            first_task_description=first_task_description,
            second_task_description=second_task_description
        )
    except KeyError as e:
        print(f"Error formatting first_QuestLLM_system_prompt: Missing key {e}")
        first_questLLM_prompt_content = "Error: Prompt formatting failed." # Set error message

    first_llm_messages = [{"role": "system", "content": first_questLLM_prompt_content}]

    if "Error:" not in first_questLLM_prompt_content:
        first_questLLM_output = get_openai_chat_completion(first_llm_messages, model=FIRST_CHAT_MODEL)
    else:
        print("Some error occured in 'first_questLLM_prompt_content'")
        return "", []

    extracted_sentence, extracted_keywords = parse_first_questLLM_output(first_questLLM_output)

    return extracted_sentence, extracted_keywords

def get_openai_chat_completion(messages: list, model: str = FIRST_CHAT_MODEL, temperature: float = 0.7) -> str:
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
    
def parse_first_questLLM_output(output: str) -> Tuple[str, list[str]]:
    try:
        data = json5.loads(output)
        return data.get("extracted_sentence", ""), data.get("extracted_keywords", [])
    except json5.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        return "", []