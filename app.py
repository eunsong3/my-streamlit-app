# app.py

import streamlit as st
from i18n import TEXT
from translator import translate
from recommender import recommend_plans
from ai_advisor import system_prompt, build_user_prompt, ask_chatgpt
from data_calculator import estimate_monthly_data

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

# ======================
# Session State
# ======================
if "page" not in st.session_state:
    st.session_state.page = "main"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "estimated_data" not in st.session_state:
    st.session_state.estimated_data = None
if "translated_texts" not in st.session_state:
    st.session_state.translated_texts = {}
if "prev_lang" not in st.session_state:
    st.session_state.prev_lang = "KO"

# ======================
# Sidebar
# ======================
st.sidebar.title(TEXT["sidebar_title"])

openai_key = st.sidebar.text_input(TEXT["openai_key"], type="password")
deepl_key = st.sidebar.text_input(TEXT["deepl_key"], type="password")

lang_label = st.sidebar.selectbox(TEXT["language"], ["한국어", "English"])
TARGET_LANG = "EN" if lang_label == "English" else "KO"

# 언어 변경 시 번역 캐시 초기화
if st.session_state.prev_lang != TARGET_LANG:
    st.session_state.translated_texts = {}
    st.session_state.prev_lang = TARGET_LANG

def t(key):
    if TARGET_LANG == "KO":
        return TEXT[key]
    if key in st.session_state.translated_texts:
        return st.session_state.translated_texts[key]
    translated = translate(TEXT[key], "EN", deepl_key)
    st.session_state.translated_texts[key] = translated
    return translated

scenario = st.sidebar.radio(
    t("scenario_title"),
    [
        t("scenario_foreign"),
        t("scenario_independent"),
        t("scenario_device")
    ]
)

if st.sidebar.button(t("data_calc_btn")):
    st.session_state.page = "calculator"

# ======================
# Calculator Page
# ======================
if st.session_state.page == "calculator":
    st.title(t("calc_title"))
    st.subheader(t("calc_subtitle"))

    hours = st.slider(t("calc_hours"), 0.0, 10.0, 2.0)
    apps = st.multiselect(t("calc_apps"), ["YouTube", "Netflix", "Instagram"])
    heavy = st.checkbox(t("calc_download"))

    if st.button(t("calc_button")):
        est = estimate_monthly_data(hours, apps, heavy)
        st.session_state.estimated_data = est
        st.success(f"{t('calc_result')} **{est}GB**")
        st.button(t("back"), on_click=lambda: setattr(st.session_state, "page", "main"))

    st.stop()

# ======================
# Main Page
# ======================
st.title(t("title"))
st.subheader(t("subtitle"))

budget = st.number_input(t("budget"), min_value=10000, step=5000)
data_usage = st.number_input(
    t("data"),
    min_value=1,
    value=st.session_state.estimated_data or 10
)

DEVICE_OPTIONS = {
    "unlocked": t("device_unlocked"),
    "subsidy": t("device_subsidy")
}

device_type = st.selectbox(
    t("device"),
    options=list(DEVICE_OPTIONS.keys()),
    format_func=lambda x: DEVICE_OPTIONS[x]
)

# ======================
# Start Chat
# ======================
if st.button(t("start")) and openai_key:
    user = {
        "budget": budget,
        "data_usage": data_usage,
        "device_type": device_type
    }

    plans = recommend_plans(user)

    st.session_state.messages = [
        {"role": "system", "content": system_prompt(TARGET_LANG)},
        {"role": "user", "content": build_user_prompt(user, scenario, plans)}
    ]

# ======================
# Chat UI
# ======================
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(
                translate(msg["content"], TARGET_LANG, deepl_key)
                if msg["role"] == "assistant"
                else msg["content"]
            )

if user_input := st.chat_input(t("chat_placeholder")):
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    reply = ask_chatgpt(st.session_state.messages, openai_key)
    reply = translate(reply, TARGET_LANG, deepl_key)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    with st.chat_message("assistant"):
        st.markdown(reply)
