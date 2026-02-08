# public_api.py

import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://openapi.epost.go.kr"
PATH = "/postal/retrieveAlddlChargeService/retrieveAlddlChargeService/getAlddlChargeList"

def fetch_mobile_plans(service_key):
    try:
        res = requests.get(
            BASE_URL + PATH,
            params={"ServiceKey": service_key, "numOfRows": 30, "pageNo": 1},
            timeout=8
        )
        res.raise_for_status()

        root = ET.fromstring(res.content)
        items = root.findall(".//alddlCharge")

        plans = []
        for item in items:
            price = item.findtext("chargeAmount", "0")
            data_mb = item.findtext("dataAmount", "0")

            if price.isdigit() and data_mb.isdigit():
                plans.append({
                    "name": item.findtext("chargeName"),
                    "price": int(price),
                    "data_gb": int(data_mb) / 1024,
                })

        if plans:
            return plans

    except Exception:
        pass

    return fallback_plans()


def fallback_plans():
    return [
        {"name": "우체국 알뜰폰 LTE 15GB", "price": 29900, "data_gb": 15},
        {"name": "우체국 알뜰폰 LTE 30GB", "price": 33000, "data_gb": 30},
        {"name": "우체국 알뜰폰 LTE 100GB", "price": 55000, "data_gb": 100},
    ]
