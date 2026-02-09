from openai import OpenAI

def chat_with_ai(messages, api_key):
    client = OpenAI(api_key=api_key)

    system = (
        "너는 통신 요금제 상담사다. "
        "아래 제공된 요금제 데이터 범위 안에서만 추천하고 "
        "존재하지 않는 요금제는 만들지 마라."
    )

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system}] + messages
    )

    return res.choices[0].message.content
