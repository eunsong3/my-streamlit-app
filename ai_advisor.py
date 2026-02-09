from openai import OpenAI

def chat_with_ai(messages, api_key, lang):
    client = OpenAI(api_key=api_key)

    system = (
        "You are a mobile plan counselor. Use only provided plan data."
        if lang == "EN"
        else
        "너는 통신 요금제 상담사이며 제공된 요금제 데이터 안에서만 추천한다."
    )

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system}] + messages
    )
    return res.choices[0].message.content
