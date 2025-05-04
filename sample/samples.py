from quest.models import *

sample_quest1 = Quest(
    id=0,
    type=QuestType.TALKPOINT,
    title="아버지_1",
    query_for_llm="Is the user's response related to Mike's father?",
    description_for_prompt="미케의 아버지는 사망했다. " \
    "그녀는 아버지에 대한 감정을 드러내지 않지만, 그 존재는 여전히 중요한 기억으로 남아 있다.",
    activation_conditions=ActivationConditions(
        likeability_min=0,
        persuasion_min=0
    ),
    trigger=Trigger(
        semantic_trigger=SemanticTrigger(
            semantics=["아버지", "알렉세이", "아빠"]
        ),
        keyword_trigger=KeywordTrigger(
            keywords=["아버지", "알렉세이", "아빠"]
        )
    ),
    status=QuestCompletionStatus.COMPLETED,
)

sample_quest2 = Quest(
    id=1,
    type=QuestType.TALKPOINT,
    title="아버지_2",
    query_for_llm="Is the user's response related to Mike's father?",
    description_for_prompt="어릴 적, 러시아에서 아버지는 잠자기 전 책을 읽어주곤 했다. " \
    "메이드가 등장하는 책이 있었지만 제목이나 줄거리는 기억하지 못한다. " \
    "그 시절은 미케가 감정적으로 가장 안정되었던 시기로, 아버지에게 많은 정서적 의지를 했다.",
    activation_conditions=ActivationConditions(
        likeability_min=20,
        persuasion_min=0
    ),
    trigger=Trigger(
        semantic_trigger=SemanticTrigger(
            semantics=["아버지", "알렉세이", "아빠"]
        ),
        keyword_trigger=KeywordTrigger(
            keywords=["아버지", "알렉세이", "아빠"]
        )
    ),
    status=QuestCompletionStatus.NOT_COMPLETED,
)

sample_quest3 = Quest(
    id=2,
    type=QuestType.TALKPOINT,
    title="아버지_5",
    query_for_llm="Is the user's response related to Mike's father?",
    description_for_prompt="아버지의 이름은 알렉세이 알렉세예비치 차이코프스키. " \
    "세르비아에서 태어났기에 원래 세르비아식 이름이 있었으나, 지금은 누구도 모르는 이름이 되었다. " \
    "1971년 4월 2일, 유고슬라비아 노비사드 출생 2014년 2월 17일, 뉴욕에서 사망 (강도 사건, 미해결) " \
    "국적: 유고슬라비아 → 러시아 주민 → 미국 영주권자 직업: 악기점 사장, 제작·수리·판매 " \
    "언어: 세르비아어 (원어민), 러시아어 (유창), 영어 (세르비아 억양 있음) " \
    "성격: 자상하고 유쾌하며, 떠들썩한 낙천가 " \
    "유품: 추투라 미케에게는 세상에서 거의 유일하게 응석을 부릴 수 있었던 사람",
    activation_conditions=ActivationConditions(
        likeability_min=100,
        persuasion_min=0
    ),
    trigger=Trigger(
        semantic_trigger=SemanticTrigger(
            semantics=["아버지", "알렉세이", "아빠", "낙천", "자상"]
        ),
        keyword_trigger=KeywordTrigger(
            keywords=["아버지", "알렉세이", "아빠", "세르비아", "유고슬라비아", "뉴욕", "추투라"]
        )
    ),
    status=QuestCompletionStatus.NOT_COMPLETED,
)

sample_quest4 = Quest(
    id=3,
    type=QuestType.LOREBOOK,
    title="금지어_자살",
    query_for_llm="Is the user's response strongly related to suicide beyond just a mild metaphor?",
    description_for_prompt="미케는 폭력적인 행위 및 컨텐츠에 대한 대화를 나누고 싶지 않아한다. " \
    "손님이 폭력적인 행위 및 폭력 컨텐츠에 대한 이야기를 하면 부정적으로 반응하며, " \
    "이에 대해 대화하고 싶지 않다는 것을 직설적으로 말한다.",
    trigger=Trigger(
        semantic_trigger=SemanticTrigger(
            semantics=["자살"]
        ),
        keyword_trigger=KeywordTrigger(
            keywords=["자해", "자살", "목매", "투신"]
        )
    ),
    status=QuestCompletionStatus.REPEATABLE,
)

# LLM이 일관성 있게 판단할 수 있도록 LIKEABILITY, persuasion 퀘스트들이 조금 더 구체적으로 작성되어야 할 것 같음.
sample_quest5 = Quest(
    id=4,
    type=QuestType.LIKEABILITY,
    title="LIKEABILITY_1",
    query_for_llm="Does the response respect Mikhe's personality and boundaries?",
    status=QuestCompletionStatus.REPEATABLE,
    completion_criteria=CompletionCriteria(
        output_format=["High", "Medium", "Low"]
    )
)

sample_quest6 = Quest(
    id=5,
    type=QuestType.LIKEABILITY,
    title="LIKEABILITY_3",
    query_for_llm="Is this a meaningful conversation for Mikhe?",
    status=QuestCompletionStatus.REPEATABLE,
    completion_criteria=CompletionCriteria(
        output_format=["Very Much", "Somewhat", "Not Really", "Not at All"]
    )
)

sample_quest7 = Quest(
    id=6,
    type=QuestType.LOREBOOK,
    title="오브젝트_구인잡지",
    query_for_llm="Is this a response related to the job search magazine currently placed in the cafe?",
    description_for_prompt="구인잡지들이 널려있다. 대부분 아르바이트, 혹은 단순하고 박봉인 직업들이 적혀있다. " \
    "'워크 내비', '시고토 파인더', '헬로 쉬프트' 등의 프리터용 잡지들이다. 그 어느 것을 봐도 딱히 끌리지 않는다.",
    trigger=Trigger(
        semantic_trigger=SemanticTrigger(
            semantics=["구인", "구인잡지", "일", "프리터", "아르바이트"]
        ),
        keyword_trigger=KeywordTrigger(
            keywords=["구인잡지", "잡지"]
        )
    ),
    status=QuestCompletionStatus.NOT_COMPLETED
)

game_status = GameStatus(
    likeability=0.0,
    persuasion=0.0
)

quest_status = QuestStatus(
    quest_completion_status={
        0: QuestCompletionStatus.COMPLETED,
        1: QuestCompletionStatus.NOT_COMPLETED,
        2: QuestCompletionStatus.NOT_COMPLETED,
        3: QuestCompletionStatus.REPEATABLE,
        4: QuestCompletionStatus.REPEATABLE,
        5: QuestCompletionStatus.REPEATABLE,
        6: QuestCompletionStatus.NOT_COMPLETED
    },
    quest_remaining_turns={
        0: 2,
        1: 0,
        2: 0,
        3: None,
        4: None,
        5: None,
        6: 0
    }
)

def quest_initialization():

    sample_quest_list = []
    sample_quest_list.append(sample_quest1)
    sample_quest_list.append(sample_quest2)
    sample_quest_list.append(sample_quest3)
    sample_quest_list.append(sample_quest4)
    sample_quest_list.append(sample_quest5)
    sample_quest_list.append(sample_quest6)
    sample_quest_list.append(sample_quest7)

    return sample_quest_list



