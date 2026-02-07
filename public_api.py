# public_api.py

import requests
import xml.etree.ElementTree as ET

URL = "http://openapi.epost.go.kr/postal/retrieveAlddlChargeService/retrieveAlddlChargeService/getAlddlChargeList"

def fetch_mobile_plans(service_key, rows=100):
    params = {
        "ServiceKey": service_key,
        "numOfRows": rows,
        "pageNo": 1
    }

    res = requests.get(URL, params=params)
    res.raise_for_status()

    root = ET.fromstring(res.content)
    plans = []

    for item in root.findall(".//AlddlCharge"):
        price = item.findtext("chargeAmount", "0")
        data_mb = item.findtext("dataAmount", "0")

        if not price.isdigit() or not data_mb.isdigit():
            continue

        plans.append({
            "carrier": item.findtext("telecomName"),
            "name": item.findtext("chargeName"),
            "price": int(price),
            "data_gb": int(data_mb) / 1024,
            "device_support": "unlocked"  # 알뜰폰 특성상 자급제
        })

    return plans
