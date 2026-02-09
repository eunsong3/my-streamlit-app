import json

DATA_PATH = "mobile_plans_2026_02.json"

def load_plans():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["plans"]

def recommend_plans(user):
    plans = load_plans()
    scored = []

    for p in plans:
        if p["monthly_fee"] > user["budget"]:
            continue

        score = 0
        if p["data_gb"] >= user["data_usage"]:
            score += 3
        if p["type"] == "mvno":
            score += 2
        if "가성비" in p["tags"]:
            score += 1

        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:3]]
