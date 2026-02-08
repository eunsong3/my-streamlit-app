# app.py

import streamlit as st
from i18n import TEXT
from translator import translate
from ai_advisor import chat_with_ai
from data_calculator import calculate_monthly_data
from device_plans import DEVICE_PLANS
from public_api import fetch_mobile_plans
from recommender import recommend_plans

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

# =====================
# Session State
# =====================
if "lang" not in st.session_state:
    st.session_state.lang = "KO"
if "translated" not in st.session_state:
    st.session_state.translated = {}
if "chat" not in st.session_state:
    st.session_state.chat = []
if "page" not in st.session_state:
    st.session_state.page = "main"

# =====================
# Sidebar
# =====================
st.sidebar.title(TEXT["sidebar_title"])

deepl_key = st.sidebar.text_input("DeepL API Key", type="password")
openai_key = st.sidebar.text_input("ChatGPT API Key", type="password")

lang_label = st.sidebar.selectbox(TEXT["language"], ["한국어", "English"])
st.session_state.lang = "EN" if lang_label == "English" else "KO"

def t(key):
    if st.session_state.lang == "KO":
        return TEXT[key]
    if key in st.session_state.translated:
        return st.session_state.translated[key]
    translated = translate(TEXT[key], "EN", deepl_key)
    st.session_state.translated[key] = translated
    return translated

if st.sidebar.button(t("calculator")):
    st.session_state.page = "calculator"

scenario = st.sidebar.radio(
    t("scenario_title"),
    [t("scenario_foreign"), t("scenario_independent"), t("scenario_device")]
)

# =====================
# 데이터 계산기 페이지
# =====================
if st.session_state.page == "calculator":
    st.title("📊 내 평균 데이터 사용량은?")
    st.subheader("평균 데이터 사용량 계산기")

    hours = st.slider("주 평균 사용시간", 1, 80, 20)
    apps = st.multiselect(
        "즐겨 사용하는 앱",
        ["SNS/메신저", "유튜브/넷플릭스", "게임", "지도/검색"]
    )
    downloads = st.checkbox("파일/앱을 자주 다운로드하나요?")

    if st.button("계산하기") and apps:
        result = calculate_monthly_data(hours, apps, downloads)
        st.success(f"예상 월 데이터 사용량: **{result}GB**")

    st.stop()

# =====================
# 메인 화면
# =====================
st.title(t("title"))
st.subheader(t("subtitle"))

budget = st.number_input(t("budget"), 10000, 70000, 30000, step=5000)
data = st.number_input(t("data"), 1, 100, 15)

# =====================
# 상담 시작
# =====================
if st.button(t("start_chat")) and openai_key:
    st.session_state.chat = [
        {
            "role": "user",
            "content": f"""
시나리오: {scenario}
예산: {budget}원
데이터 사용량: {data}GB

이 조건에 맞는 요금제를 추천해줘.
"""
        }
    ]

# =====================
# 채팅 UI
# =====================
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(
            translate(msg["content"], st.session_state.lang, deepl_key)
        )

if prompt := st.chat_input(t("chat_placeholder")):
    st.session_state.chat.append({"role": "user", "content": prompt})

    answer = chat_with_ai(
        st.session_state.chat,
        openai_key,
        st.session_state.lang
    )

    st.session_state.chat.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.markdown(
            translate(answer, st.session_state.lang, deepl_key)
        )
