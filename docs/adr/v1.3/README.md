# ADR v1.3 - 심사 대비 개선

## Overview

v1.3은 해커톤 심사에서 지적될 수 있는 **3가지 핵심 비판점**을 해결합니다.

## ADR List

| ADR | Title | Status | Problem |
|-----|-------|--------|---------|
| [ADR-106](./ADR-106-citation-transparency.md) | Citation Transparency | Accepted | 지식 인용 불투명 |
| [ADR-107](./ADR-107-twin-differentiation.md) | Twin Differentiation | Accepted | 트윈 차별화 부족 |

## Summary

### ADR-106: Citation Transparency

**문제**: 업로드 지식이 답변에 실제로 사용되는지 확인 불가

**해결**:
- `AnswerResult` 스키마에 `citations` 필드 추가
- `ReviewResult` 스키마에 `keyword_matches` 필드 추가
- UI에 "📚 참고된 지식" expander 추가

### ADR-107: Twin Differentiation

**문제**: 트윈 출력이 동일한 템플릿 → "캐릭터만 다른 것" 오해

**해결**:
- `ResponseFormat` 데이터클래스 추가
- 트윈별 고유 섹션 구조 정의 (CEO: 결론→근거, PM: 체크리스트 등)
- Mock/Claude/OpenAI 응답 포맷 차별화

## Files Changed

```
schemas/response.py          NEW   Citation, AnswerResult, ReviewResult
core/citation.py             NEW   find_relevant_knowledge, extract_keyword_context
core/orchestrator.py         MOD   answer_with_citations, route_and_answer
core/evaluation.py           MOD   review_with_evidence
agents.py                    MOD   ResponseFormat, 트윈별 포맷 정의
llm_client.py                MOD   트윈별 차별화 응답 생성
app.py                       MOD   Citation/Keyword Match UI
README.md                    MOD   Deployment 섹션 추가
```

## SOLID Principles Applied

| Principle | Implementation |
|-----------|----------------|
| **SRP** | Citation 로직을 `core/citation.py`로 분리 |
| **OCP** | 새 매칭 알고리즘/트윈 추가 시 확장 가능 |
| **LSP** | 모든 트윈이 TwinAgent 인터페이스 준수 |
| **DIP** | Pydantic 스키마에 의존 |
