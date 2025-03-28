import requests
import os

API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_URL = "https://api.anthropic.com/v1/complete"

candidate_models = [
    "claude-v1",
    "claude-1",
    "claude-instant-1",
    "claude-2",
    "claude-2.0",
    "claude-2.1",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
]

for model in candidate_models:
    print(f"Trying model: {model}")
    prompt = "\n\nHuman: Say hello\n\nAssistant:"
    headers = {
        "x-api-key": API_KEY,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens_to_sample": 10,
        "temperature": 0.0,
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        print(f"✅ Access granted to model: {model}")
        print("Response:", response.json())
        break  # Stop after first working model
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ Model not found: {model}")
        elif e.response.status_code == 401:
            print("❌ Invalid API key or permission denied.")
            break
        else:
            print(f"❌ Error for model {model}:", e.response.text)
    except Exception as ex:
        print(f"❌ General error for model {model}: {ex}")