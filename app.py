# app.py

import streamlit as st
from scenario import classify_user
from recommender import recommend_plans
from ai_advisor import build_system_prompt, build_user_prompt, ask_chatgpt
from i18n import TEXT

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

# =========================
# Sidebar
# =========================
st.sidebar.title("🔐 API & Language")

openai_api_key = st.sidebar.text_input("ChatGPT API Key", type="password")
language = st.sidebar.selectbox("Language", ["한국어", "English"])

T = TEXT[language]

# =========================
# Session State
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# UI
# =========================
st.title(T["title"])
st.subheader(T["subtitle"])

budget = st.number_input(T["budget"], min_value=10000, step=5000)
data_usage = st.number_input(T["data"], min_value=1)
ott_apps = st.multiselect(T["ott"], ["Netflix", "YouTube", "Wavve"])
device_type = st.selectbox(T["device"], ["자급제", "공시지원금"])

is_foreigner = st.checkbox(T["foreigner"])
want_new_device = st.checkbox(T["new_device"])

# =========================
# Start Chat
# =========================
if st.button(T["start"]) and openai_api_key:
    user = {
        "budget": budget,
        "data_usage": data_usage,
        "ott_apps": ott_apps,
        "device_type": device_type,
        "is_foreigner": is_foreigner,
        "want_new_device": want_new_device
    }

    scenario = classify_user(user)
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

# =========================
# Chat Input
# =========================
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
