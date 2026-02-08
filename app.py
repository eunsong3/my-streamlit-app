# app.py

import streamlit as st
from i18n import TEXT
from translator import translate
from public_api import fetch_mobile_plans
from recommender import recommend_plans
from ai_advisor import ask_chatgpt

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

# ===== Session State =====
if "lang" not in st.session_state:
    st.session_state.lang = "KO"
if "translated" not in st.session_state:
    st.session_state.translated = {}

def t(key):
    if key not in TEXT:
        return key
    if st.session_state.lang == "KO":
        return TEXT[key]
    if key in st.session_state.translated:
        return st.session_state.translated[key]
    translated = translate(TEXT[key], "EN", deepl_key)
    st.session_state.translated[key] = translated
    return translated

# ===== Sidebar =====
st.sidebar.title(t("sidebar_title"))

openai_key = st.sidebar.text_input(t("openai_key"), type="password")
deepl_key = st.sidebar.text_input(t("deepl_key"), type="password")
public_key = st.sidebar.text_input(t("public_key"), type="password")

lang_label = st.sidebar.selectbox(t("language"), ["한국어", "English"])
st.session_state.lang = "EN" if lang_label == "English" else "KO"

scenario = st.sidebar.radio(
    t("scenario_title"),
    [
        t("scenario_foreign"),
        t("scenario_device"),
        t("scenario_independent")
    ]
)

# ===== Main =====
st.title(t("title"))
st.subheader(t("subtitle"))

budget = st.number_input(t("budget"), min_value=10000, step=5000)
data_usage = st.number_input(t("data"), min_value=1)

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

    answer = ask_chatgpt(recommended, user, openai_key, st.session_state.lang)
    answer = translate(answer, st.session_state.lang, deepl_key)

    with st.chat_message("assistant"):
        st.markdown(answer)
