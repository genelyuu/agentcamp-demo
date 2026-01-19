# ADR-107: Twin Differentiation

## Status
Accepted

## Date
2026-01-19

## Context

해커톤 심사에서 다음과 같은 비판이 예상됨:

> "Digital Twin이 라우팅 + 공통 템플릿으로 보인다.
> 트윈은 캐릭터만 다른 것 아닌가?"

현재 상태:
- `MockLLMClient`: 모든 트윈이 동일한 응답 포맷 사용
- 트윈별 차별화: 이름, 역할, 스타일 텍스트만 다름
- 출력 구조는 동일 → "템플릿" 인상

## Decision

**트윈별 고유 응답 포맷을 정의하고 적용한다.**

### 1. ResponseFormat 데이터클래스 (`agents.py`)

```python
@dataclass
class ResponseFormat:
    greeting: str = ""
    sections: List[str] = field(default_factory=list)
    closing: str = ""
    emoji: str = ""
    tone: str = "professional"
```

### 2. 트윈별 응답 포맷 정의

| Twin | Emoji | Sections | Tone |
|------|-------|----------|------|
| **Sam Lee (CEO)** | 🎯 | 결론 → 근거 → 리스크 → 다음 액션 | direct |
| **JH Kim (PM)** | 📋 | 문제 정의 → 성공 조건 → 체크리스트 → 우선순위 | friendly |
| **Seul Kim (FE)** | 🎨 | 사용자 흐름 → 에러 케이스 → 구현 포인트 → 개선 제안 | friendly |
| **Jin Park (BE)** | 🔧 | 현상 분석 → 원인 가설 → 검증 방법 → 해결 방안 | analytical |

### 3. MockLLMClient 업데이트 (`llm_client.py`)

```python
def generate_response(self, twin, org, knowledge, question) -> str:
    fmt = twin.response_format

    # 트윈별 이모지 + 인사말
    lines.append(f"{fmt.emoji} [{twin.name} | {twin.role}]")
    if fmt.greeting:
        lines.append(fmt.greeting)

    # 트윈별 섹션 구조
    for section in fmt.sections:
        lines.append(f"**{section}**")
        lines.append(self._generate_section_content(twin.name, section))

    # 트윈별 클로징
    lines.append(fmt.closing)
```

### 4. LLM 클라이언트 시스템 프롬프트 업데이트

```python
# Claude/OpenAI 시스템 프롬프트에 포맷 지시 추가
[응답 포맷]
{emoji} 시작하고, 다음 섹션 구조를 따르세요:
1. 결론
2. 근거
3. 리스크
4. 다음 액션

마무리: 빠르게 움직이세요.
톤: direct
```

## Consequences

### Positive
- 같은 질문에도 트윈별로 **확연히 다른 출력 구조**
- 심사위원이 "각 트윈이 실제로 다르게 동작한다"고 인식
- 신입 사용자가 역할별 특성을 체감

### Negative
- Mock 응답 코드 복잡도 증가
- 트윈 추가 시 포맷도 정의해야 함

### SOLID 원칙
- **SRP**: 트윈 정의와 응답 포맷 분리
- **OCP**: 새 트윈 추가 시 ResponseFormat만 정의
- **LSP**: 모든 트윈이 동일한 TwinAgent 인터페이스 준수

## Example Output Comparison

### 질문: "이 장애 원인을 어떻게 확인하나요?"

**Sam Lee (CEO) - 🎯 direct tone**
```
🎯 [Sam Lee | CEO/대표]

📝 질문: 이 장애 원인을 어떻게 확인하나요?

**1. 결론**
→ 고객 가치가 명확하면 진행, 불명확하면 검증부터

**2. 근거**
→ 비용/속도/품질 중 우선순위를 정해서 판단

**3. 리스크**
→ 리스크는 회피가 아닌 관리 대상

**4. 다음 액션**
→ 오늘 중 검증 가능한 최소 단위로 실행

⚠️ 주의: 고객가치가 분명하면 추진

빠르게 움직이세요.
```

**Jin Park (BE) - 🔧 analytical tone**
```
🔧 [Jin Park | Backend]

📝 질문: 이 장애 원인을 어떻게 확인하나요?

**1. 현상 분석**
→ 로그/메트릭에서 관찰된 현상 정리
  • 언제 발생? • 빈도는? • 영향 범위는?

**2. 원인 가설**
→ 가능한 원인 나열:
  1) 가설A: _____
  2) 가설B: _____

**3. 검증 방법**
→ 각 가설을 검증할 방법:
  • 로그 쿼리: _____
  • 재현 단계: _____

**4. 해결 방안**
→ 단기 해결 vs 장기 개선 분리
  • 핫픽스: _____
  • 근본 해결: _____

⚠️ 주의: 재현가능한 증거(로그/메트릭) 우선

로그와 메트릭으로 확인하세요.
```
