import json
import re

DATA_PATH = "mobile_plans.json"

def parse_data_amount(data_str):
    if "무제한" in data_str:
        return 999
    match = re.search(r"(\\d+)GB", data_str)
    return int(match.group(1)) if match else 0

def load_plans():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def recommend_plans(user):
    plans = load_plans()
    scored = []

    for p in plans:
        if p["price"] > user["budget"]:
            continue

        data_gb = parse_data_amount(p["data"])
        score = 0

        if data_gb >= user["data_usage"]:
            score += 3
        if "알뜰폰" in p["type"]:
            score += 1
        if "온라인" in p["type"]:
            score += 1

        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:3]]
