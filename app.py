# app.py (발췌)

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
language = st.sidebar.selectbox(
    "Language",
    ["한국어", "English"]
)

T = TEXT[language]

st.sidebar.title(T["sidebar_title"])

openai_api_key = st.sidebar.text_input(
    T["api_key"],
    type="password"
)

st.sidebar.markdown(f"### {T['scenario_title']}")
scenario = st.sidebar.radio(
    T["scenario_label"],
    [
        T["scenario_1"],
        T["scenario_2"],
        T["scenario_3"]
    ]
)

st.sidebar.markdown("---")

if st.sidebar.button(T["data_calc_btn"]):
    st.session_state.page = "calculator"

# =========================
# Calculator Page
# =========================
if st.session_state.page == "calculator":
    st.title(T["calc_title"])
    st.subheader(T["calc_subtitle"])

    hours = st.slider(
        T["calc_hours"],
        0.0, 10.0, 2.0
    )

    apps = st.multiselect(
        T["calc_apps"],
        ["YouTube", "Netflix", "Instagram", "Web Browsing"]
    )

    heavy_download = st.checkbox(T["calc_download"])

    if st.button(T["calc_button"]):
        estimated = estimate_monthly_data(hours, apps, heavy_download)
        st.session_state.estimated_data = estimated
        st.success(f"{T['calc_result']} **{estimated}GB**")

        st.button(
            T["back"],
            on_click=lambda: setattr(st.session_state, "page", "main")
        )

    st.stop()

# =========================
# Main Page
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

if user_input := st.chat_input(T["chat_placeholder"]):
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
