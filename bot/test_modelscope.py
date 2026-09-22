import os
import requests

token = os.environ.get('MODEL_SCOPE_API_KEY', '')
print(f"Token: {token[:8]}...")

url = "https://api-inference.modelscope.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

payload = {
    "model": "Qwen/Qwen3.5-27B",
    "messages": [
        {"role": "user", "content": "Отзыв: Пароочиститель мощный, отлично чистит! Напиши короткий вежливый ответ от бренда LOWENGRASS."}
    ],
    "max_tokens": 150,
    "temperature": 0.7
}

r = requests.post(url, json=payload, headers=headers, timeout=30)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    text = r.json()['choices'][0]['message']['content']
    print(f"\n✅ Ответ Qwen:\n{text[:400]}")
else:
    print(f"Ошибка: {r.text[:300]}")
