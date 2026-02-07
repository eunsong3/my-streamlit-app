# app.py

import streamlit as st
from recommender import recommend_plans
from ai_advisor import build_system_prompt, build_user_prompt, ask_chatgpt
from i18n import TEXT
from data_calculator import estimate_monthly_data

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

# =========================
# Session State
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "estimated_data" not in st.session_state:
    st.session_state.estimated_data = None

if "page" not in st.session_state:
    st.session_state.page = "main"

# =========================
# Sidebar
# =========================
st.sidebar.title("⚙️ 설정")

language = st.sidebar.selectbox("Language", ["한국어", "English"])
T = TEXT[language]

openai_api_key = st.sidebar.text_input("ChatGPT API Key", type="password")

st.sidebar.markdown("### 👤 사용자 시나리오")
scenario = st.sidebar.radio(
    "시나리오 선택",
    ["외국인 유학생", "경제적 자립 신입생", "기기 교체 희망 신입생"]
)

st.sidebar.markdown("---")

if st.sidebar.button("📊 평균 데이터 사용량 계산기"):
    st.session_state.page = "calculator"

# =========================
# 📊 데이터 계산기 페이지
# =========================
if st.session_state.page == "calculator":
    st.title("📊 내 평균 데이터 사용량은?")
    st.subheader("평균 데이터 사용량 계산기")

    hours = st.slider(
        "와이파이가 없는 환경에서의 평균 휴대폰 사용시간 (시간/일)",
        0.0, 10.0, 2.0
    )

    apps = st.multiselect(
        "즐겨 사용하는 앱",
        ["YouTube", "Netflix", "Instagram", "웹서핑"]
    )

    heavy_download = st.checkbox("파일/앱을 자주 다운로드하나요?")

    if st.button("📈 내 데이터 사용량 계산하기"):
        estimated = estimate_monthly_data(hours, apps, heavy_download)
        st.session_state.estimated_data = estimated

        st.success(f"👉 예상 월 데이터 사용량은 약 **{estimated}GB** 입니다.")
        st.button("⬅ 상담으로 돌아가기", on_click=lambda: setattr(st.session_state, "page", "main"))

    st.stop()

# =========================
# 🏠 Main 상담 페이지
# =========================
st.title(T["title"])
st.subheader(T["subtitle"])

budget = st.number_input(T["budget"], min_value=10000, step=5000)

data_usage = st.number_input(
    T["data"],
    min_value=1,
    value=st.session_state.estimated_data or 10
)

device_type = st.selectbox(T["device"], ["자급제", "공시지원금"])

# =========================
# 상담 시작
# =========================
if st.button(T["start"]) and openai_api_key:
    user = {
        "budget": budget,
        "data_usage": data_usage,
        "device_type": device_type,
        "scenario": scenario
    }

    plans = recommend_plans(user)

    system_prompt = build_system_prompt(language)
    user_prompt = build_user_prompt(user, scenario, plans)

    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

# =========================
# Chat UI
# =========================
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if user_input := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    reply = ask_chatgpt(
        st.session_state.messages,
        openai_api_key
    )

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    with st.chat_message("assistant"):
        st.markdown(reply)
