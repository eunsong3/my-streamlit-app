# translator.py

import requests

DEEPL_URL = "https://api-free.deepl.com/v2/translate"

def translate(text, target_lang, api_key):
    if not api_key or target_lang == "KO":
        return text

    response = requests.post(
        DEEPL_URL,
        headers={"Authorization": f"DeepL-Auth-Key {api_key}"},
        data={"text": text, "target_lang": target_lang}
    )
    response.raise_for_status()
    return response.json()["translations"][0]["text"]
