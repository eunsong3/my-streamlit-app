# ai_advisor.py

from openai import OpenAI

def ask_chatgpt(plans, user, api_key, lang):
    client = OpenAI(api_key=api_key)

    plan_text = "\n".join(
        [f"- {p['name']} ({p['price']}원 / {p['data_gb']}GB)" for p in plans]
    )

    system = (
        "You are a mobile plan expert helping students in Korea."
        if lang == "EN"
        else "너는 신입생을 돕는 통신비 전문 상담가야."
    )

    prompt = f"""
사용자 시나리오: {user['scenario']}
월 예산: {user['budget']}원
월 데이터 사용량: {user['data_usage']}GB

추천 요금제:
{plan_text}

시나리오를 고려해서 왜 이 요금제가 적합한지 설명해줘.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )

    return res.choices[0].message.content
