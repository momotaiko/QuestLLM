from typing import List
from quest.models import *
from quest.io.loader import save_quests
from sentence_transformers import SentenceTransformer, models
import numpy as np
from config.environment import QUEST_JSON_PATH

# 캐시 시스템 아직 구현 안함
# # 전역 캐시 (LRU 방식)
# embedding_cache = OrderedDict()
# CACHE_SIZE = 100  # 캐싱할 최대 임베딩 개수

MODEL_CONFIGS = {
    "paraphrase-multilingual-mpnet-base-v2": {
        "load_direct": True,
        "model_name": "paraphrase-multilingual-mpnet-base-v2"
    },
    "LaBSE": {
        "load_direct": True,
        "model_name": "sentence-transformers/LaBSE"
    },
    "multilingual-e5-large-instruct": {
        "load_direct": False,
        "model_name": "intfloat/multilingual-e5-large",
        "pooling": "mean",
        "max_seq_length": 512
    },
    "BGE-M3": {
        "load_direct": False,
        "model_name": "BAAI/bge-m3",
        "pooling": "cls",
        "max_seq_length": 8192
    },
    "Nomic-Embed": {
        "load_direct": False,
        "model_name": "nomic-ai/nomic-embed-text-v1",
        "pooling": "mean",
        "max_seq_length": 8192
    }
}

class Retriever:
    def __init__(self, device='cpu', model_key='paraphrase-multilingual-mpnet-base-v2'):
        self.device = device
        config = MODEL_CONFIGS.get(model_key)

        if config is None:
            raise ValueError(f"This model key is not defined in MODEL_CONFIG.")
        
        if config.get("load_direct", False):
            # 모델을 직접 로드할 수 있는 경우
            self.embedder = SentenceTransformer(config["model_name"], device=device)
        else:
            # pooling layer 직접 조립해서 사용하기
            transformer = models.Transformer(
                model_name_or_path=config["model_name"],
                max_seq_length=config.get("max_seq_length", 512),
                device=device
            )
            pooling_mode = config.get("pooling", "mean")
            if pooling_mode == "mean":
                pooling = models.Pooling(
                    # Returns the number of dimensions in the output of SentenceTransformer.encode()
                    transformer.get_word_embedding_dimension(),
                    pooling_mode_mean_tokens=True,
                    pooling_mode_cls_token=False
                )
            elif pooling_mode == "cls":
                pooling = models.Pooling(
                    transformer.get_word_embedding_dimension(),
                    pooling_mode_cls_token=True
                )
            else:
                pooling = models.Pooling(
                    transformer.get_word_embedding_dimension(),
                    pooling_mode_mean_tokens=True,
                    pooling_mode_cls_token=False
                )
            self.embedder = SentenceTransformer(modules=[transformer, pooling])

    def embed(self, texts: List[str]) -> List[List[float]]:
        # 주어진 문자열 리스트를 임베딩 텐서로 변환
        embeddings = self.embedder.encode(texts, convert_to_tensor=False, device=self.device)
        return [embedding.tolist() for embedding in embeddings]
    
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

def cosine_similarity(a, b):
    """Calculates cosine similarity between two vectors."""

    vec_a = np.asarray(a)
    vec_b = np.asarray(b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0 
    return np.dot(vec_a, vec_b) / (norm_a * norm_b)

def calculate_similarities(quests: List[Quest], query_embedding: List[float]) -> List[float]:

    # 트리거 임베딩 벡터의 평균을 구해 쿼리와 유사도 비교 vs 각 트리거 임베딩 벡터와 쿼리간의 유사도의 평균
    # 어떤거 쓸지는 좀 더 실험이 필요할 듯. 일단은 내적 후 평균(정보 보존, 정밀도 높음)
    
    similarities = []
    for quest in quests:
        skip_evaluation = (
            quest.status == QuestCompletionStatus.REPEATABLE
            and quest.type in {QuestType.LIKEABILITY, QuestType.PERSUASION}
        )
                            
        if skip_evaluation:
            similarities.append(0.0)
            continue

        if not quest.trigger.semantic_trigger or not quest.trigger.semantic_trigger.embeddings:
            similarities.append(0.0)
            continue

        similarity = []
        for trigger_embedding in quest.trigger.semantic_trigger.embeddings:
            similarity.append(cosine_similarity(query_embedding, trigger_embedding))

        similarities.append(np.mean(similarity))

    return similarities
    
def contextual_search(quests: List[Quest],
                      extracted_sentence: str, 
                      game_status: GameStatus, 
                      quest_status: QuestStatus,
                      top_k: int = 5,
                      retriever: Optional[Retriever] = None) -> List[int]:
    
    if isinstance(extracted_sentence, str):
        extracted_sentence = [extracted_sentence]

    # ------------------------------------------------------------------------
    # 나중에 서버 코드와 통합할 때 retriever는 questLLM 밖에서 의존성을 주입받도록 수정
    retriever = retriever or Retriever() 
    # ------------------------------------------------------------------------

    query_embedding = retriever.embed(extracted_sentence)[0]

    # 필요하다면 임베딩 벡터로 변환한 후 저장
    is_there_new_embedding = False
    for quest in quests:
        skip_evaluation = (
            quest.status == QuestCompletionStatus.REPEATABLE
            and quest.type in {QuestType.LIKEABILITY, QuestType.PERSUASION}
        )
        
        if skip_evaluation:
            continue

        semantic_trigger = quest.trigger.semantic_trigger
        if semantic_trigger and semantic_trigger.semantics \
            and not (semantic_trigger.embeddings and len(semantic_trigger.embeddings) > 0):
            semantic_trigger.embeddings = retriever.embed(semantic_trigger.semantics)
            is_there_new_embedding = True
    
    if is_there_new_embedding:
        save_quests(QUEST_JSON_PATH, quests) 

    similarities = calculate_similarities(quests, query_embedding)

    actual_k = min(top_k, len(quests))
    sorted_indices = np.argsort(similarities)[::-1]

    top_k_retrieved_quest_ids = []
    for idx in sorted_indices:
        quest = quests[idx]
        if is_quest_activated(quest, game_status, quest_status):
            top_k_retrieved_quest_ids.append(quest.id)
        if len(top_k_retrieved_quest_ids) >= actual_k:
            break

    return top_k_retrieved_quest_ids






        

    
    





