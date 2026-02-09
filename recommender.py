import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "mobile_plans.json")

def parse_data_amount(data_str):
    if not isinstance(data_str, str):
        return 0
    if "무제한" in data_str:
        return 999
    match = re.search(r"(\d+)GB", data_str)
    return int(match.group(1)) if match else 0

def load_plans():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ✅ JSON 구조 자동 판별
    if isinstance(data, dict) and "plans" in data:
        return data["plans"]
    elif isinstance(data, list):
        return data
    else:
        return []

def recommend_plans(user):
    plans = load_plans()
    scored = []

    for p in plans:
        # 🔒 방어 코드 (혹시 모를 데이터 이상 방지)
        if not isinstance(p, dict):
            continue
        if "price" not in p or "data" not in p:
            continue

        if p["price"] > user["budget"]:
            continue

        data_gb = parse_data_amount(p["data"])
        score = 0

        # 데이터 충족 여부
        if data_gb >= user["data_usage"]:
            score += 3

        # 온라인/알뜰 가중치 (합리적 선택 유도)
        if "알뜰폰" in p.get("type", ""):
            score += 1
        if "온라인" in p.get("type", ""):
            score += 1

        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:3]]
