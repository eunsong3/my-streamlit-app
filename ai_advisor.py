# ai_advisor.py

def generate_prompt(user, scenario, plans):
    plan_text = "\n".join(
        [f"- {p['name']} : 월 {p['price']}원 / {p['data_gb']}GB" for p in plans]
    )

    prompt = f"""
너는 통신비 전문 상담가이자 대학교 선배야.

[사용자 유형]
{scenario}

[사용자 정보]
- 월 예산: {user['budget']}원
- 월 데이터 사용량: {user['data_usage']}GB
- 주요 OTT: {", ".join(user['ott_apps']) if user['ott_apps'] else "없음"}
- 단말 유형: {user['device_type']}

[추천 요금제 TOP 3]
{plan_text}

단통법 폐지 이후 기준으로,
초보자도 이해할 수 있도록
왜 이 요금제가 좋은지 설명해줘.
"""
    return prompt
