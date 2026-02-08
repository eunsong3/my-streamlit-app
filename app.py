# app.py

import streamlit as st
from i18n import TEXT
from translator import translate
from public_api import fetch_mobile_plans
from recommender import recommend_plans
from ai_advisor import ask_chatgpt

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

# ======================
# Session State
# ======================
if "lang" not in st.session_state:
    st.session_state.lang = "KO"
if "translated" not in st.session_state:
    st.session_state.translated = {}

# ======================
# Sidebar
# ======================
st.sidebar.title(TEXT["sidebar_title"])

openai_key = st.sidebar.text_input(TEXT["openai_key"], type="password")
deepl_key = st.sidebar.text_input(TEXT["deepl_key"], type="password")
public_key = st.sidebar.text_input(TEXT["public_key"], type="password")

lang_label = st.sidebar.selectbox(TEXT["language"], ["한국어", "English"])
TARGET_LANG = "EN" if lang_label == "English" else "KO"

# 언어 바뀔 때만 번역 캐시 초기화
if TARGET_LANG != st.session_state.lang:
    st.session_state.lang = TARGET_LANG
    st.session_state.translated = {}

def t(key):
    if TARGET_LANG == "KO":
        return TEXT[key]
    if key in st.session_state.translated:
        return st.session_state.translated[key]
    translated = translate(TEXT[key], "EN", deepl_key)
    st.session_state.translated[key] = translated
    return translated

scenario = st.sidebar.radio(
    t("scenario_title"),
    [
        t("scenario_foreign"),
        t("scenario_device"),
        t("scenario_independent")
    ]
)

# ======================
# Main UI
# ======================
st.title(t("title"))
st.subheader(t("subtitle"))

budget = st.number_input(t("budget"), min_value=10000, step=5000)
data_usage = st.number_input(t("data"), min_value=1)

# ======================
# Run Recommendation
# ======================
if st.button(t("start")) and openai_key:
    plans = fetch_mobile_plans(public_key)

    user = {
        "budget": budget,
        "data_usage": data_usage,
        "scenario": scenario
    }

    recommended = recommend_plans(user, plans)

    st.markdown("### ✅ 추천 요금제")
    for p in recommended:
        st.success(f"{p['name']} | {p['price']}원 | {p['data_gb']}GB")

    answer = ask_chatgpt(recommended, user, openai_key, TARGET_LANG)
    answer = translate(answer, TARGET_LANG, deepl_key)

    with st.chat_message("assistant"):
        st.markdown(answer)
