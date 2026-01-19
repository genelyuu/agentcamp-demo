"""
app.py - Streamlit UI 메인 엔트리포인트
책임: Admin / New Hire / Dashboard 모드 UI 렌더링
ADR-101: UI/Core Boundary Separation - UI-only 레이어
ADR-106: Citation Transparency - 지식 인용 표시
ADR-108: Explainable Routing - 라우팅 근거 표시
ADR-109: Structured Rubric Scoring - 4칸 체크리스트 표시
ADR-110: Offline-first + LLM-enhanced 아키텍처
"""
import streamlit as st

from core import (
    get_org,
    set_org,
    get_knowledge,
    set_knowledge,
    get_sessions,
    set_sessions,
    route_agent,
    route_agent_with_reason,
    answer_with_twin,
    route_and_answer,
    set_llm_client,
    simple_review,
    review_with_evidence,
    rubric_review,
    get_active_knowledge_top3,
    render_twin_answer,
)
from agents import get_twins
from ingestion import extract_knowledge

# 페이지 설정
st.set_page_config(
    page_title="AgentCamp (Veluga) - OJT Digital Twins Demo",
    layout="wide"
)

# 데이터 로드
ORG = get_org()
KNOW = get_knowledge()
SESS = get_sessions()
TWINS = get_twins()


def ensure_user(user_id: str) -> None:
    """사용자 세션 초기화"""
    if user_id not in SESS["users"]:
        SESS["users"][user_id] = {
            "name": user_id,
            "position": "",
            "adapt_score": 50,
            "risk_score": 50,
            "tasks_done": 0,
            "questions": 0,
            "last_task": None,
        }


def pick_knowledge_snippet() -> str:
    """최근 지식 스니펫 반환"""
    items = KNOW.get("items", [])
    if not items:
        return ""
    return items[-1]["text"]


# ============================================================
# Sidebar
# ============================================================
st.sidebar.title("AgentCamp 데모")
mode = st.sidebar.radio("모드", ["Admin(회사 세팅)", "New Hire(OJT)", "Dashboard(HR)"])
user_id = st.sidebar.text_input("신입 사용자 ID", value="minsu")
ensure_user(user_id)

# LLM 설정
st.sidebar.divider()
st.sidebar.subheader("LLM 설정")

# Session state 초기화
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "mock"
if "llm_connected" not in st.session_state:
    st.session_state.llm_connected = False

llm_provider = st.sidebar.selectbox(
    "LLM Provider",
    ["mock", "claude", "openai"],
    index=["mock", "claude", "openai"].index(st.session_state.llm_provider),
    help="mock: API 키 없이 동작 / claude: Anthropic Claude / openai: OpenAI GPT"
)

api_key = ""
model_name = ""

if llm_provider != "mock":
    api_key = st.sidebar.text_input(
        "API Key",
        type="password",
        help="Anthropic 또는 OpenAI API 키를 입력하세요"
    )

    if llm_provider == "claude":
        model_name = st.sidebar.selectbox(
            "Model",
            ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
            help="Claude 모델 선택"
        )
    else:  # openai
        model_name = st.sidebar.selectbox(
            "Model",
            ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            help="OpenAI 모델 선택"
        )

if st.sidebar.button("LLM 적용"):
    try:
        set_llm_client(llm_provider, api_key if api_key else None, model_name if model_name else None)
        st.session_state.llm_provider = llm_provider
        st.session_state.llm_connected = True
        if llm_provider == "mock":
            st.sidebar.success("Mock 모드 활성화")
        else:
            st.sidebar.success(f"{llm_provider.upper()} 연결 완료!")
    except Exception as e:
        st.sidebar.error(f"연결 실패: {str(e)}")
        st.session_state.llm_connected = False

# 현재 LLM 상태 표시
if st.session_state.llm_connected:
    st.sidebar.caption(f"현재: {st.session_state.llm_provider.upper()} 모드")


# ============================================================
# Admin Mode
# ============================================================
if mode == "Admin(회사 세팅)":
    st.header("Admin Console - Veluga OJT 설정")

    col1, col2 = st.columns(2)

    with col1:
        company = st.text_input("회사명", value=ORG.get("company", "Veluga"))
        role = st.text_input("OJT 직무", value=ORG.get("role", "Project Manager"))
        tools = st.text_input(
            "도구(콤마로)",
            value=",".join(ORG.get("tools", ["Slack", "GitHub"]))
        )

    with col2:
        st.subheader("기본 평가 루브릭(데모)")
        st.caption("실제 서비스에선 직무별 루브릭 템플릿 + 회사별 커스텀")
        keywords = st.text_input(
            "완료 기준 키워드(콤마)",
            value="원인,재현,재발방지,로그"
        )

    if st.button("저장"):
        new_org = {
            "company": company.strip(),
            "role": role.strip(),
            "tools": [t.strip() for t in tools.split(",") if t.strip()],
            "rubric": {
                "acceptance_keywords": [k.strip() for k in keywords.split(",") if k.strip()]
            },
        }
        set_org(new_org)
        st.success("회사 설정 저장 완료! (org.json)")

    st.divider()
    st.subheader("데이터 수집 파이프라인(데모)")
    st.caption("회의 STT / Slack-Discord 대화 / 고객미팅 STT를 업로드하면 지식으로 적재됩니다.")

    source = st.selectbox("소스 타입", ["meeting_stt", "slack_discord", "client_stt"])
    uploaded = st.file_uploader("텍스트 파일 업로드(.txt)", type=["txt"])
    raw_text = st.text_area("또는 텍스트 붙여넣기", height=150)

    if st.button("지식 추출 & 저장"):
        text = ""
        if uploaded is not None:
            text = uploaded.read().decode("utf-8", errors="ignore")
        else:
            text = raw_text

        if not text.strip():
            st.warning("텍스트가 비었습니다.")
        else:
            new_items = extract_knowledge(source, text)
            KNOW["items"].extend(new_items)
            set_knowledge(KNOW)
            st.success(f"{len(new_items)}개 지식 항목 저장 완료!")
            st.write(new_items[:5])

    st.divider()
    st.subheader("📚 Active Knowledge Top-3 (KNOW-008)")
    st.caption("각 태그별 최근 1개 지식을 표시합니다. 질문 응답 시 우선 참조됩니다.")

    knowledge_items = KNOW.get("items", [])
    if knowledge_items:
        active_top3 = get_active_knowledge_top3(knowledge_items)
        if active_top3:
            cols = st.columns(len(active_top3))
            for idx, (tag, items) in enumerate(active_top3.items()):
                with cols[idx]:
                    st.markdown(f"**{tag.upper()}**")
                    for item in items:
                        text_preview = item.get("text", "")[:80]
                        source = item.get("source", "unknown")
                        st.caption(f"[{source}] {text_preview}...")
        else:
            st.info("태그별 지식이 아직 없습니다.")
    else:
        st.info("저장된 지식이 없습니다. 위에서 텍스트를 업로드해주세요.")

    st.divider()
    st.subheader("현재 지식(최근 10개)")
    for it in KNOW.get("items", [])[-10:]:
        st.write(f"- [{it['source']}/{it['tag']}] {it['text']}")


# ============================================================
# New Hire Mode
# ============================================================
elif mode == "New Hire(OJT)":
    st.header("New Hire - OJT 실행")

    user = SESS["users"][user_id]
    position_str = f" | 직책: {user.get('position')}" if user.get("position") else ""
    st.info(f"회사: {ORG.get('company')} | 직무: {ORG.get('role')} | 사용자: {user_id}{position_str}")

    # 1) 오늘의 미션
    st.subheader("1) 오늘의 미션(업무)")
    if user.get("last_task") is None or st.button("오늘 미션 새로 받기"):
        task = {
            "title": "로그 기반 장애 원인 요약",
            "context": "최근 배포 이후 500 에러가 증가. 원인을 추정하고 재발 방지안을 제시.",
            "deliverable": "원인(가설) 1개 이상 + 재현 조건 + 재발 방지 1개 + 참고 로그 키워드",
            "acceptance_keywords": ORG.get("rubric", {}).get(
                "acceptance_keywords", ["원인", "재현", "재발방지", "로그"]
            ),
        }
        user["last_task"] = task
        set_sessions(SESS)

    task = user["last_task"]
    if task:
        st.write(f"**미션:** {task['title']}")
        st.write(f"- 상황: {task['context']}")
        st.write(f"- 제출물: {task['deliverable']}")
        st.caption(f"완료 키워드(데모): {', '.join(task['acceptance_keywords'])}")

    # 2) 질문하기
    st.subheader("2) 질문하기 (Digital Twins)")
    q = st.text_input(
        "질문 입력",
        placeholder="예: 이 장애 원인 확인을 위해 어떤 로그를 봐야 하나요?"
    )
    if st.button("질문 보내기") and q.strip():
        user["questions"] += 1

        # ADR-108: Explainable Routing - 라우팅 근거 포함
        routing_result = route_agent_with_reason(q, TWINS)

        # ADR-106: Citation Transparency - 인용 정보 포함 응답
        knowledge_items = KNOW.get("items", [])
        result = route_and_answer(TWINS, ORG, knowledge_items, q)

        set_sessions(SESS)

        # 라우팅 정보 표시 (ADR-108)
        st.markdown(f"### 라우팅: **{result.routed_to}** ({routing_result.confidence_percent}% 신뢰도)")

        # 라우팅 근거 표시
        with st.expander("🎯 라우팅 근거 (ADR-108)", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**매칭된 키워드**")
                if routing_result.matched_keywords:
                    for kw in routing_result.matched_keywords[:5]:
                        st.markdown(f"- `{kw}`")
                else:
                    st.caption("매칭된 키워드 없음 (기본 라우팅)")

            with col2:
                st.markdown("**대안 후보**")
                if routing_result.has_alternatives:
                    for alt in routing_result.alternatives[:3]:
                        st.markdown(f"- {alt.name} ({alt.confidence_percent}%)")
                else:
                    st.caption("대안 없음")

            st.caption(f"📋 {routing_result.format_reason_display()}")

        # 트윈별 구조화된 응답 (ADR-108)
        twin = TWINS.get(result.routed_to)
        if twin:
            structured_answer = render_twin_answer(twin, result.answer)
            st.markdown(structured_answer.to_markdown())
        else:
            st.code(result.answer)

        # 참고된 지식 표시 (ADR-106)
        if result.has_citations:
            with st.expander(f"📚 참고된 지식 ({len(result.citations)}건)", expanded=True):
                for i, cite in enumerate(result.citations, 1):
                    relevance_pct = int(cite.relevance_score * 100)
                    st.markdown(f"**[{i}] {cite.source} / {cite.tag}** (관련도: {relevance_pct}%)")
                    st.caption(cite.text)
        else:
            st.caption("ℹ️ 아직 업로드된 지식이 없어 기본 응답을 제공합니다. Admin 모드에서 지식을 추가해보세요.")

    # 3) 제출 & 리뷰
    st.subheader("3) 제출하기 → 리뷰 받기")
    submission = st.text_area(
        "제출 내용",
        height=160,
        placeholder="원인/재현조건/재발방지/로그 키워드를 포함해 작성"
    )
    if st.button("제출 & 리뷰") and submission.strip() and task:
        # ADR-106: Citation Transparency - 키워드 매칭 근거 포함 리뷰
        review_result = review_with_evidence(task, submission)

        # ADR-109: Structured Rubric Scoring - 4칸 구조 평가
        rubric_result = rubric_review(submission)

        user["tasks_done"] += 1
        user["adapt_score"] = min(100, user["adapt_score"] + int(review_result.score * 0.1))
        user["risk_score"] = max(0, user["risk_score"] - int(review_result.score * 0.05))
        set_sessions(SESS)

        # 점수 및 등급 표시
        st.success(f"리뷰 점수: **{rubric_result.total_score}점** (등급: {rubric_result.grade})")

        # 4칸 체크리스트 표시 (ADR-109)
        st.markdown("### 📋 4칸 구조 평가 (ADR-109)")
        cols = st.columns(4)

        for idx, col_data in enumerate(rubric_result.columns):
            with cols[idx]:
                # 칸 헤더
                status_icon = "✅" if col_data.score >= 20 else "⚠️" if col_data.score >= 10 else "❌"
                st.markdown(f"**{col_data.display_name}** {status_icon}")
                st.metric("점수", f"{col_data.score}/25")

                # 체크리스트 항목
                for item in col_data.items:
                    if item.checked:
                        st.markdown(f"✅ {item.label}")
                    else:
                        st.markdown(f"❌ {item.label}")

        # 종합 피드백
        st.divider()
        st.markdown("### 종합 피드백")
        st.info(rubric_result.overall_feedback)

        # 누락된 요소
        if rubric_result.missing_elements:
            with st.expander("⚠️ 누락된 요소", expanded=True):
                for elem in rubric_result.missing_elements:
                    st.markdown(f"- {elem}")

        # 기존 키워드 매칭 상세 (ADR-106)
        with st.expander(
            f"🔍 키워드 매칭 상세 ({review_result.matched_count}/{review_result.total_keywords})",
            expanded=False
        ):
            for km in review_result.keyword_matches:
                if km.matched:
                    st.markdown(f"✅ **{km.keyword}** - 매칭됨")
                    if km.context:
                        st.caption(f"   → \"{km.context}\"")
                else:
                    st.markdown(f"❌ **{km.keyword}** - 누락")

        st.write("**다음 스텝**")
        st.write(review_result.next_step)


# ============================================================
# Dashboard Mode
# ============================================================
else:
    st.header("HR Dashboard - OJT 진행 현황")

    users = SESS.get("users", {})
    user_count = len(users)

    # 메트릭 계산
    avg_adapt = int(sum(u["adapt_score"] for u in users.values()) / max(1, user_count))
    avg_risk = int(sum(u["risk_score"] for u in users.values()) / max(1, user_count))
    total_tasks = sum(u["tasks_done"] for u in users.values())

    # 메트릭 표시
    cols = st.columns(4)
    cols[0].metric("신입 수", user_count)
    cols[1].metric("평균 적응도", avg_adapt)
    cols[2].metric("평균 리스크", avg_risk)
    cols[3].metric("총 완료 업무", total_tasks)

    # 개별 현황
    st.subheader("개별 현황")
    for uid, u in users.items():
        with st.expander(
            f"{uid} | adapt={u['adapt_score']} risk={u['risk_score']} "
            f"tasks={u['tasks_done']} q={u['questions']}"
        ):
            st.write(u)
