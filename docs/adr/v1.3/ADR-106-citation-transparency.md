# ADR-106: Citation Transparency

## Status
Accepted

## Date
2026-01-19

## Context

해커톤 심사에서 다음과 같은 비판이 예상됨:

> "업로드된 지식이 실제로 답변/리뷰에 사용되는지 확인할 수 없다.
> 업로드는 이벤트고, 답변은 템플릿일 수 있다."

현재 상태:
- `answer_with_twin()`: 지식 스니펫을 받아서 답변 생성
- UI: 답변만 표시, 어떤 지식이 사용되었는지 불투명

## Decision

**지식 인용(Citation) 투명성을 구현한다.**

### 1. 스키마 정의 (`schemas/response.py`)

```python
class Citation(BaseModel):
    knowledge_id: str
    text: str
    source: str
    tag: str
    relevance_score: float

class AnswerResult(BaseModel):
    answer: str
    routed_to: str
    citations: List[Citation]

class KeywordMatch(BaseModel):
    keyword: str
    matched: bool
    context: Optional[str]

class ReviewResult(BaseModel):
    score: int
    strengths: List[str]
    improvements: List[str]
    keyword_matches: List[KeywordMatch]
```

### 2. Citation 서비스 (`core/citation.py`)

```python
def find_relevant_knowledge(question, knowledge_items) -> (List[Citation], str):
    """질문과 관련된 지식 찾기 + 인용 정보 생성"""

def extract_keyword_context(text, keyword) -> str:
    """키워드 주변 컨텍스트 추출"""
```

### 3. Orchestrator 확장 (`core/orchestrator.py`)

```python
def answer_with_citations(twin, org, knowledge_items, question) -> AnswerResult:
    """답변 + 인용 정보 포함"""

def route_and_answer(twins, org, knowledge_items, question) -> AnswerResult:
    """라우팅 + 답변 + 인용 통합"""
```

### 4. Evaluation 확장 (`core/evaluation.py`)

```python
def review_with_evidence(task, submission) -> ReviewResult:
    """키워드 매칭 근거 포함 리뷰"""
```

### 5. UI 업데이트 (`app.py`)

```python
# 답변 후
with st.expander("📚 참고된 지식"):
    for cite in result.citations:
        st.markdown(f"**{cite.source}/{cite.tag}** (관련도: {cite.relevance_score})")
        st.caption(cite.text)

# 리뷰 후
with st.expander("🔍 키워드 매칭 상세"):
    for km in review_result.keyword_matches:
        if km.matched:
            st.markdown(f"✅ **{km.keyword}** - 매칭됨")
            st.caption(km.context)
        else:
            st.markdown(f"❌ **{km.keyword}** - 누락")
```

## Consequences

### Positive
- 심사위원이 "지식 → 답변" 연결을 즉시 확인 가능
- 신입 사용자가 어떤 지식이 참고되었는지 학습 가능
- 리뷰 근거의 투명성 확보

### Negative
- 코드 복잡도 증가 (새 스키마, 서비스 추가)
- 약간의 성능 오버헤드 (지식 검색)

### SOLID 원칙
- **SRP**: Citation 로직을 별도 모듈로 분리
- **OCP**: 새로운 매칭 알고리즘 추가 시 확장 가능
- **DIP**: Pydantic 스키마에 의존
