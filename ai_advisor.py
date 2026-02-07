# ai_advisor.py

from openai import OpenAI

def build_system_prompt(language):
    if language == "English":
        return "You are a friendly mobile plan expert helping students in Korea."
    return "너는 신입생을 돕는 친절한 통신비 전문 상담가야."

def build_user_prompt(user, scenario, plans):
    plan_text = "\n".join(
        [f"- {p['name']} ({p['price']}원 / {p['data_gb']}GB)" for p in plans]
    )

    return f"""
[User Scenario]
{scenario}

[Conditions]
- Budget: {user['budget']}
- Data Usage: {user['data_usage']}GB

[Recommended Plans]
{plan_text}

Please explain why these plans are suitable.
"""

def ask_chatgpt(messages, api_key):
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content
