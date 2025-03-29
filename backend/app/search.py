''' For scaling search, consider OpenSearch with indexing and a reranker. 
For highest accuracy, a full RAG pipeline could be used (higher infra cost)'''

'''approach 1(full doc search): here we use fuzzy search + LLM (that would be costlier), has better context
so would answer even arbitrary ques, but might miss details, however we have extracted those already.
It is also expensive and slow if alot of queries come in

approach 2(searching the postgres): faster querying and could introduce filters as well. dosen't work
well for contexual questions

approach 3(hybrid): might go with this. first search sql if the answer is there, if not, then fallback to full
search.

For increased volume would batch N documents and send a bulk prompt

code optimzations:
Woudl use smaller chunks (sliding window/top 3 results)
Would use token truncation and summarization pre-step for large docs
Would  add session cacheing to maintain chat context'''
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
import os
import requests
from app.s3_utils import get_s3_documents, get_s3_file_content

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

EXTRACTED_TEXTS_FOLDER = "extractedtexts/"

#search documents in S3 using fuzzy matching
def search_documents(query: str, email: str):
    documents = get_s3_documents(email)
    print(f"\n Fetched {len(documents)} documents for {email}: {documents}")

    results = []

    for doc_name in documents:
        s3_key = f"{EXTRACTED_TEXTS_FOLDER}{doc_name}"
        file_content = get_s3_file_content(s3_key)
        print(f"\nReading file: {s3_key}")
        print(f"Content size: {len(file_content)} characters")

        if not file_content.strip():
            print("Skipping empty file.")
            continue

        lines = file_content.split("\n")
        top_score = 0
        for line in lines:
            line_score = fuzz.partial_ratio(query, line)
            if line_score > top_score:
                top_score = line_score
        print(f"Top score for {doc_name}: {top_score}")

        if top_score > 50:
            relevant_text = extract_relevant_text(file_content, query)
            results.append({
                "document_name": doc_name,
                "relevant_text": relevant_text,
                "score": top_score
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    print(f"\nReturning {len(results)} matching documents.")
    return results

#Function to extract relevant text for the query
def extract_relevant_text(doc_text: str, query: str):
    lines = doc_text.split("\n")  # split
    relevant_text = ""
    for line in lines:
        if fuzz.partial_ratio(query, line) > 50:  # comparing query to each line using fuzzy matching
            relevant_text += line + "\n"
    return relevant_text

# function to generate an answer from the relevant document content
def generate_answer(relevant_text: str, query: str):
    prompt = f"Answer the following question based on the text below:\n\nText:\n{relevant_text}\n\nQuestion: {query}\nAnswer:"

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    data = {
        "model": "claude-3-opus-20240229",  
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