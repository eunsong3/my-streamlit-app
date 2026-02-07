# ai_advisor.py

from openai import OpenAI

def build_system_prompt(language):
    if language == "English":
        return (
            "You are a mobile plan expert and a friendly senior student in Korea. "
            "Explain mobile plans clearly for freshmen and international students."
        )
    return (
        "너는 통신비 전문 상담가이자 친절한 대학교 선배야. "
        "신입생과 외국인 유학생이 이해하기 쉽게 설명해줘."
    )

def build_user_prompt(user, scenario, plans):
    plan_text = "\n".join(
        [f"- {p['name']} ({p['price']}원 / {p['data_gb']}GB)" for p in plans]
    )

    return f"""
[사용자 유형]
{scenario}

[조건]
- 예산: {user['budget']}원
- 데이터 사용량: {user['data_usage']}GB
- 단말 유형: {user['device_type']}

[추천 요금제]
{plan_text}

왜 이 요금제가 적합한지 설명해줘.
"""

def ask_chatgpt(messages, api_key):
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content
