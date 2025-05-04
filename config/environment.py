from dotenv import load_dotenv
import os

load_dotenv()

# OAI 키
API_KEY = os.getenv("API_KEY")

# 1stQuestLLM 모델
FIRST_CHAT_MODEL = os.getenv("FIRST_CHAT_MODEL")

# 2ndQuestLLM 모델
SECOND_CHAT_MODEL = os.getenv("SECOND_CHAT_MODEL")

# 퀘스트들이 저장되는 경로
QUEST_JSON_PATH = os.getenv("QUEST_JSON_PATH")

# 샘플 대화기록이 저장된 경로
CONVERSATION_SAMPLE_PATH = os.getenv("CONVERSATION_SAMPLE_PATH")

# 한번 활성화된 로어가 몇 턴 동안 유지될지
LORE_REMAINING_DURATION = int(os.getenv("LORE_REMAINING_DURATION"))