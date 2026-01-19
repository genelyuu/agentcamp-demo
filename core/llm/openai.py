"""
core/llm/openai.py - OpenAI Capability 구현
CAP-008: Capability별 OpenAI 구현
ADR-104: LLM Capability Interface
SEC-002: API 오류 메시지 일반화
"""
from typing import Any, Dict, List
from uuid import uuid4
from datetime import datetime

from agents import TwinAgent
from schemas import KnowledgeItem, KnowledgeTag, KnowledgeSource, OJTTask
from .error_handler import format_error_response, sanitize_error


class OpenAIRouter:
    """OpenAI 라우팅 Capability - GPT-4o-mini 모델 사용"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("openai 패키지를 설치하세요: pip install openai")

    def route(self, question: str) -> str:
        """LLM 기반 Twin 라우팅"""
        system_prompt = """당신은 질문을 분석하여 가장 적합한 멘토를 선택하는 라우터입니다.

선택 가능한 멘토:
1. Sam Lee (CEO/대표): 우선순위, 전략, 고객, 리스크, 비용 관련
2. JH Kim (PM): 요구사항, 스코프, 정의, KPI, 지표 관련
3. Seul Kim (Frontend): UI/UX, 화면, 프론트엔드, 컴포넌트, 반응형 관련
4. Jin Park (Backend): API, DB, Infra, 성능, 안정성, 로그, 기본값

질문을 분석하고 가장 적합한 멘토 이름만 정확히 반환하세요.
예: "Sam Lee" 또는 "JH Kim" 또는 "Seul Kim" 또는 "Jin Park"
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=50,
                temperature=0
            )
            result = response.choices[0].message.content.strip()

            # 유효한 이름인지 검증
            valid_names = ["Sam Lee", "JH Kim", "Seul Kim", "Jin Park"]
            for name in valid_names:
                if name in result:
                    return name

            return "Jin Park"  # 기본값
        except Exception:
            return "Jin Park"


class OpenAIAnswerer:
    """OpenAI 응답 Capability - GPT-4o 모델 사용"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("openai 패키지를 설치하세요: pip install openai")

    def answer(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str,
        question: str
    ) -> str:
        """OpenAI 기반 응답 생성"""
        system_prompt = self._build_system_prompt(twin, org, knowledge)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=1024,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return format_error_response(e, "openai")

    def _build_system_prompt(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str
    ) -> str:
        return f"""당신은 {org.get('company', 'Veluga')} 회사의 {twin.name}입니다.

[역할] {twin.role}
[커뮤니케이션 스타일] {twin.style}

[책임 영역]
{chr(10).join(f'- {r}' for r in twin.responsibilities)}

[의사결정 규칙]
{chr(10).join(f'- {r}' for r in twin.decision_rules)}

[회사 지식/컨텍스트]
{knowledge if knowledge else '(없음)'}

[지시사항]
- 신입 직원의 OJT를 돕는 멘토 역할을 합니다.
- 질문에 대해 당신의 역할과 스타일에 맞게 답변하세요.
- 구체적이고 실행 가능한 조언을 제공하세요.
- 한국어로 답변하세요."""


class OpenAIExtractor:
    """OpenAI 추출 Capability - GPT-4o-mini 모델 사용"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("openai 패키지를 설치하세요: pip install openai")

    def extract(self, source: str, text: str) -> List[KnowledgeItem]:
        """OpenAI 기반 지식 추출"""
        system_prompt = """텍스트에서 OJT에 유용한 지식을 추출하세요.

각 지식 항목은 다음 형식으로 출력하세요:
[TAG] 내용

TAG는 다음 중 하나:
- RULE: 규칙, 원칙, 필수 사항
- PITFALL: 주의사항, 흔한 실수, 함정
- GLOSSARY: 용어 정의, 약어 설명
- PROCESS: 절차, 단계, 워크플로우

예시:
[RULE] 배포 전 반드시 staging 환경에서 테스트해야 합니다.
[PITFALL] API 키를 코드에 하드코딩하면 보안 문제가 발생합니다.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=2048,
                temperature=0.3
            )
            result = response.choices[0].message.content
            return self._parse_response(source, result)
        except Exception:
            return []

    def _parse_response(self, source: str, response: str) -> List[KnowledgeItem]:
        """응답 파싱하여 KnowledgeItem 리스트 생성"""
        items = []

        try:
            source_enum = KnowledgeSource(source)
        except ValueError:
            source_enum = KnowledgeSource.MEETING_STT

        tag_map = {
            "RULE": KnowledgeTag.RULE,
            "PITFALL": KnowledgeTag.PITFALL,
            "GLOSSARY": KnowledgeTag.GLOSSARY,
            "PROCESS": KnowledgeTag.PROCESS,
        }

        for line in response.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            for tag_str, tag_enum in tag_map.items():
                if line.startswith(f"[{tag_str}]"):
                    content = line[len(f"[{tag_str}]"):].strip()
                    if content:
                        items.append(KnowledgeItem(
                            id=f"k-{uuid4().hex[:8]}",
                            text=content[:1000],
                            tag=tag_enum,
                            source=source_enum,
                            created_at=datetime.utcnow()
                        ))
                    break

        return items


class OpenAIJudge:
    """OpenAI 평가 Capability - GPT-4o 모델 사용"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("openai 패키지를 설치하세요: pip install openai")

    def judge(self, task: OJTTask, submission: str) -> Dict[str, Any]:
        """OpenAI 기반 제출물 평가"""
        system_prompt = f"""당신은 OJT 제출물을 평가하는 리뷰어입니다.

[미션]
- 제목: {task.title}
- 상황: {task.context}
- 제출물 요구사항: {task.deliverable}
- 완료 기준 키워드: {', '.join(task.acceptance_keywords)}

[평가 기준]
1. 완료 기준 키워드 포함 여부 (50점)
2. 설명의 구체성과 근거 (30점)
3. 실행 가능성 (20점)

[출력 형식]
SCORE: (0-100 숫자)
STRENGTHS:
- 강점 1
- 강점 2
IMPROVEMENTS:
- 개선점 1
- 개선점 2
NEXT_STEP: 다음 스텝 안내
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"제출물:\n{submission}"}
                ],
                max_tokens=1024,
                temperature=0.5
            )
            result = response.choices[0].message.content
            return self._parse_response(result)
        except Exception as e:
            return {
                "score": 50,
                "strengths": [],
                "improvements": [f"평가 중 오류 발생: {sanitize_error(e)}"],
                "next_step": "다시 시도해주세요."
            }

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """응답 파싱하여 평가 결과 생성"""
        result: Dict[str, Any] = {
            "score": 50,
            "strengths": [],
            "improvements": [],
            "next_step": ""
        }

        lines = response.strip().split("\n")
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("SCORE:"):
                try:
                    score_str = line.replace("SCORE:", "").strip()
                    result["score"] = min(100, max(0, int(score_str)))
                except ValueError:
                    pass
            elif line == "STRENGTHS:":
                current_section = "strengths"
            elif line == "IMPROVEMENTS:":
                current_section = "improvements"
            elif line.startswith("NEXT_STEP:"):
                result["next_step"] = line.replace("NEXT_STEP:", "").strip()
                current_section = None
            elif line.startswith("- ") and current_section:
                result[current_section].append(line[2:])

        return result
