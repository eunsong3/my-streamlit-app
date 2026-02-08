# public_api.py

import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://openapi.epost.go.kr"
PATH = "/postal/retrieveAlddlChargeService/retrieveAlddlChargeService/getAlddlChargeList"

def fetch_mobile_plans(service_key, rows=30):
    url = BASE_URL + PATH

    params = {
        "ServiceKey": service_key,
        "numOfRows": rows,
        "pageNo": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except Exception:
        # 👉 Streamlit Cloud에서 실패하면 여기로 옴
        return fallback_plans()

    try:
        root = ET.fromstring(response.content)
    except Exception:
        return fallback_plans()

    items = root.findall(".//alddlCharge")
    plans = []

    for item in items:
        price = item.findtext("chargeAmount", "0")
        data_mb = item.findtext("dataAmount", "0")

        if not price.isdigit() or not data_mb.isdigit():
            continue

        plans.append({
            "name": item.findtext("chargeName"),
            "price": int(price),
            "data_gb": int(data_mb) / 1024,
            "device_support": "unlocked"
        })

    if not plans:
        return fallback_plans()

    return plans


def fallback_plans():
    # 👉 실제 우체국 알뜰폰 요금제 예시 기반 더미
    return [
        {
            "name": "우체국 알뜰폰 LTE 15GB",
            "price": 29900,
            "data_gb": 15,
            "device_support": "unlocked"
        },
        {
            "name": "우체국 알뜰폰 LTE 30GB",
            "price": 33000,
            "data_gb": 30,
            "device_support": "unlocked"
        },
        {
            "name": "우체국 알뜰폰 LTE 100GB",
            "price": 55000,
            "data_gb": 100,
            "device_support": "unlocked"
        }
    ]
