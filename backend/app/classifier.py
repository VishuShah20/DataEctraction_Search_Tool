'''Have used a combo of zero-shot classifier and fallback to LLM if complex, this gives faster and lightweight processing,
but if contexual accuracy is very important would just go with an LLM 
(also using a classifier in house might lead us to outdated tech as LLMs these days are improving quick)
Might consider using LLMs if cost dosen't really matter mmuch

Also currently anthropic API calls are repeated across the codebase (generate_answer, classify_document).
To improve that we would create `AnthropicClient` class. Single place to manage headers, model version,
cleaner and easier to update and cache
'''
from transformers import pipeline
import requests
import os
from dotenv import load_dotenv

load_dotenv()

zero_shot_classifier = pipeline("zero-shot-classification")
candidate_labels = ["invoice", "contract", "purchase order"]

CONFIDENCE_THRESHOLD = 0.7 #zero-shot

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/complete"
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

def classify_document(text: str) -> str:
    """
    Primary classification function.
    Uses zero-shot pipeline first; if confidence is below the threshold, fall back to Anthropic.
    """
    #Zero-shot classification
    result = zero_shot_classifier(text, candidate_labels)
    top_label = result["labels"][0]       #top predicted label
    top_score = result["scores"][0]       # Confidence score for top label

    print(f"[Zero-shot] top_label={top_label}, score={top_score:.4f}")

    #Check confidence threshold
    if top_score < CONFIDENCE_THRESHOLD:
        print(f"[Zero-shot] Confidence below {CONFIDENCE_THRESHOLD}, calling Anthropic fallback...")
        # Fallback to Anthropic if zero-shot confidence is too low
        anthropic_label = anthropic_fallback_classification(text)
        print(f"[Anthropic] Fallback label={anthropic_label}")
        return anthropic_label
    else:
        print(f"[Zero-shot] Confidence above {CONFIDENCE_THRESHOLD}, returning {top_label}")
        return top_label


def anthropic_fallback_classification(text: str) -> str:
    if not ANTHROPIC_API_KEY:
        return "No API key found"

    categories_str = ", ".join(candidate_labels)
    system_prompt = (
        f"You are a top-tier classification expert. The possible document types are: {categories_str}.\n"
        f"Classify the document content below into one of these categories based on its content.\n"
        f"Respond with ONLY the document type label. No explanation, no extra text — just one or two words.\n"
        f"If the document doesn't fit the categories, return the best-guess type (still one or two words max)."
    )

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 100,
        "temperature": 0.2,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": text}
        ]
    }

    try:
        response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        message = result.get("content", [])
        if message and isinstance(message, list) and "text" in message[0]:
            classification = message[0]["text"].strip()
            print("[Anthropic] Response:", classification)
            return classification
        else:
            print("[Anthropic] Unexpected response format:", result)
            return "Unknown"
    except Exception as e:
        print("Anthropic fallback error:", e)
        return "Error"