# app.py

import streamlit as st
from i18n import TEXT
from translator import translate
from public_api import fetch_mobile_plans
from recommender import recommend_plans
from ai_advisor import ask_chatgpt

st.set_page_config(page_title="Y-Mobile Saver", layout="wide")

st.sidebar.title(TEXT["sidebar_title"])

openai_key = st.sidebar.text_input(TEXT["openai_key"], type="password")
deepl_key = st.sidebar.text_input(TEXT["deepl_key"], type="password")
public_key = st.sidebar.text_input(TEXT["public_key"], type="password")

lang = st.sidebar.selectbox(TEXT["language"], ["한국어", "English"])
TARGET_LANG = "EN" if lang == "English" else "KO"

def t(text):
    return translate(text, TARGET_LANG, deepl_key)

st.title(t(TEXT["title"]))
st.subheader(t(TEXT["subtitle"]))

budget = st.number_input(t(TEXT["budget"]), min_value=10000, step=5000)
data_usage = st.number_input(t(TEXT["data"]), min_value=1)

device_type = "unlocked"

if st.button(t(TEXT["start"])) and openai_key and public_key:
    try:
        with st.spinner("공공데이터 요금제 불러오는 중..."):
            plans = fetch_mobile_plans(public_key)
    except RuntimeError as e:
        st.error(str(e))
        st.stop()

    user = {
        "budget": budget,
        "data_usage": data_usage,
        "device_type": device_type
    }

    recommended = recommend_plans(user, plans)

    st.markdown("### ✅ 추천 요금제")
    for p in recommended:
        st.success(f"{p['name']} | {p['price']}원 | {round(p['data_gb'],1)}GB")

    answer = ask_chatgpt(recommended, user, openai_key, TARGET_LANG)
    answer = translate(answer, TARGET_LANG, deepl_key)

    with st.chat_message("assistant"):
        st.markdown(answer)
