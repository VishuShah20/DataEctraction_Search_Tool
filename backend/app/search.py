from fuzzywuzzy import fuzz
from dotenv import load_dotenv
import os
import requests
from app.s3_utils import get_s3_documents, get_s3_file_content

# Load environment variables
load_dotenv()

# Anthropic API key and endpoint
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

EXTRACTED_TEXTS_FOLDER = "extractedtexts/"

# Function to search documents in S3 using fuzzy matching
def search_documents(query: str, email: str):
    documents = get_s3_documents(email)
    print(f"\n📂 Fetched {len(documents)} documents for {email}: {documents}")

    results = []

    for doc_name in documents:
        s3_key = f"{EXTRACTED_TEXTS_FOLDER}{doc_name}"
        file_content = get_s3_file_content(s3_key)
        print(f"\n📄 Reading file: {s3_key}")
        print(f"📑 Content size: {len(file_content)} characters")

        if not file_content.strip():
            print("⚠️ Skipping empty file.")
            continue

        lines = file_content.split("\n")
        top_score = 0
        for line in lines:
            line_score = fuzz.partial_ratio(query, line)
            if line_score > top_score:
                top_score = line_score
        print(f"🔍 Top score for {doc_name}: {top_score}")

        if top_score > 50:
            relevant_text = extract_relevant_text(file_content, query)
            results.append({
                "document_name": doc_name,
                "relevant_text": relevant_text,
                "score": top_score
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    print(f"\n✅ Returning {len(results)} matching documents.")
    return results

# Function to extract relevant text for the query
def extract_relevant_text(doc_text: str, query: str):
    lines = doc_text.split("\n")  # Split the text into lines (or use paragraphs)
    relevant_text = ""
    for line in lines:
        if fuzz.partial_ratio(query, line) > 50:  # Compare query to each line using fuzzy matching
            relevant_text += line + "\n"
    return relevant_text

# Function to generate an answer from the relevant document content using Anthropic's Claude 3 model
def generate_answer(relevant_text: str, query: str):
    prompt = f"Answer the following question based on the text below:\n\nText:\n{relevant_text}\n\nQuestion: {query}\nAnswer:"

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    data = {
        "model": "claude-3-opus-20240229",  # Claude model
        "max_tokens": 1000,
        "temperature": 0.7,
        "system": "You are a helpful assistant that answers questions based on text.",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        if 'content' in result and isinstance(result['content'], list):
            answer = result['content'][0].get('text', '')
            return answer.strip()
        else:
            print("Error: Invalid response structure")
            return "Sorry, I couldn't generate an answer."
    except requests.exceptions.RequestException as e:
        print(f"Error generating answer: {e}")
        return "Sorry, I couldn't generate an answer."