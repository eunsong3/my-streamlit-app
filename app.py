import streamlit as st
from recommender import recommend_plans
from device_plans import DEVICE_PLANS
from ai_advisor import chat_with_ai

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

# =====================
# Session State
# =====================
if "chat" not in st.session_state:
    st.session_state.chat = []
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
if "recommended_plans" not in st.session_state:
    st.session_state.recommended_plans = []

# =====================
# Sidebar
# =====================
st.sidebar.title("⚙️ 설정")
openai_key = st.sidebar.text_input("ChatGPT API Key", type="password")

scenario = st.sidebar.radio(
    "사용자 시나리오",
    ["외국인 유학생", "경제적 자립 준비 학생", "기기 교체 희망 학생"]
)

st.title("📱 Y-Mobile Saver")

# =====================
# 기기 교체 시나리오 (기존 유지)
# =====================
if scenario == "기기 교체 희망 학생":
    st.subheader("📱 기기 교체 요금제 추천")

    maker = st.selectbox("제조사", ["애플", "삼성"])

    if maker == "애플":
        model = st.selectbox("기종", ["아이폰 17 (256GB)"])
    else:
        model = st.selectbox(
            "기종",
            ["갤럭시 S25", "갤럭시 Z 플립7 (256GB)"]
        )

    price = st.selectbox("요금 수준", ["~4만원", "~5만원", "~6만원"])

    key = (maker, model, price)

    if key in DEVICE_PLANS:
        for name, fee, discount, support in DEVICE_PLANS[key]:
            st.success(
                f"{name}\n"
                f"- 월 요금: {fee}원\n"
                f"- 선택약정(2년): {discount}원\n"
                f"- 기기변경 지원금: {support}원"
            )
    else:
        st.info("선택한 조건에 대한 요금제 정보가 준비되어 있지 않습니다.")

    st.stop()

# =====================
# JSON 기반 요금제 추천 (외국인 / 경제적 자립)
# =====================
st.subheader("📊 요금제 추천")

budget = st.number_input(
    "월 예산 (원)",
    min_value=10000,
    max_value=150000,
    value=40000,
    step=5000
)

data = st.number_input(
    "월 데이터 사용량 (GB)",
    min_value=1,
    max_value=500,
    value=20
)

# =====================
# 상담 시작
# =====================
if st.button("💬 상담 시작하기") and openai_key:
    user = {
        "budget": budget,
        "data_usage": data,
        "scenario": scenario
    }

    recommended = recommend_plans(user)

    # 추천 요금제 저장
    st.session_state.recommended_plans = recommended

    # AI가 기억하도록 요약 생성
    plan_summary = "\n".join([
        f"- {p['carrier']} {p['name']} / {p['price']}원 / 데이터 {p['data']} / 혜택: {p['benefits']}"
        for p in recommended
    ])

    st.session_state.chat = [
        {
            "role": "system",
            "content": (
                "너는 통신 요금제 전문 상담사다.\n"
                "아래 추천된 요금제 정보를 기억하고,\n"
                "사용자의 질문에 이 요금제들을 기준으로 답변하라.\n\n"
                f"[추천 요금제 목록]\n{plan_summary}"
            )
        },
        {
            "role": "user",
            "content": (
                f"나는 {scenario}이야.\n"
                f"월 예산은 {budget}원이고\n"
                f"월 데이터 사용량은 {data}GB야.\n"
                f"이 조건에 맞는 요금제를 추천해줘."
            )
        }
    ]

    st.session_state.chat_started = True

# =====================
# 추천 요금제 항상 표시 (채팅 중에도 유지)
# =====================
if st.session_state.recommended_plans:
    st.subheader("📌 추천 요금제 (상담 중 유지)")
    for p in st.session_state.recommended_plans:
        st.success(
            f"{p['carrier']} | {p['name']} | {p['price']}원\n"
            f"데이터: {p['data']}\n"
            f"혜택: {p['benefits']}"
        )

# =====================
# Chat UI (연속 대화)
# =====================
if st.session_state.chat_started:
    for msg in st.session_state.chat:
        if msg["role"] in ["user", "assistant"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("추천 요금제에 대해 궁금한 점을 물어보세요"):
        st.session_state.chat.append(
            {"role": "user", "content": prompt}
        )

        answer = chat_with_ai(
            st.session_state.chat,
            openai_key
        )

        st.session_state.chat.append(
            {"role": "assistant", "content": answer}
        )

        with st.chat_message("assistant"):
            st.markdown(answer)

# =====================
# Disclaimer
# =====================
st.caption(
    "⚠️ 본 요금제 정보는 2026년 2월 기준이며 "
    "실제 가입 시 통신사에서 최신 조건을 확인하세요."
)
