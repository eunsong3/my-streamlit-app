# ai_advisor.py

from openai import OpenAI

def system_prompt(lang):
    if lang == "EN":
        return "You are a friendly mobile plan advisor helping students in Korea."
    return "너는 신입생을 돕는 친절한 통신비 전문 상담가야."

def build_user_prompt(user, scenario, plans):
    plan_text = "\n".join(
        [f"- {p['name']} ({p['price']}원 / {p['data_gb']}GB)" for p in plans]
    )

    return f"""
[사용자 시나리오]
{scenario}

[조건]
- 예산: {user['budget']}원
- 데이터 사용량: {user['data_usage']}GB

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
