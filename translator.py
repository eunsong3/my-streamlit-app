# translator.py

import requests

DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"

def translate_text(text, target_lang, api_key):
    headers = {
        "Authorization": f"DeepL-Auth-Key {api_key}"
    }

    data = {
        "text": text,
        "target_lang": target_lang
    }

    response = requests.post(DEEPL_API_URL, headers=headers, data=data)
    response.raise_for_status()

    result = response.json()
    return result["translations"][0]["text"]
