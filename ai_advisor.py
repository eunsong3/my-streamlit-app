# ai_advisor.py

from openai import OpenAI

def chat_with_ai(messages, api_key, lang):
    client = OpenAI(api_key=api_key)

    system = (
        "You are a friendly mobile plan counselor for students. "
        "Explain difficult terms in simple language."
        if lang == "EN"
        else
        "너는 대학 신입생을 돕는 친절한 통신 요금제 상담사야. "
        "모르는 용어가 나오면 쉽게 풀어서 설명해줘."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system}] + messages
    )

    return response.choices[0].message.content
