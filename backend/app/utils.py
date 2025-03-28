import fitz  # PyMuPDF
import os
import requests
from dotenv import load_dotenv
import re
from app.database import insert_invoice_data, insert_purchase_order_data
import json

# Load environment variables
load_dotenv()

# Anthropic API key and endpoint
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a PDF document.
    """
    document = fitz.open(pdf_path)
    text = ""

    # Loop through the pages and extract text
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()  # Extract text from each page
    
    return text

def extract_invoice_details_with_anthropic(text: str, document_type: str):
    """
    Extract key details for invoices using Anthropic's LLM.
    """
    prompt = f"""
    Extract the following details from the invoice document below:
    1. Invoice Number
    2. Invoice Date
    3. Total Amount
    4. Vendor Name
    
    Document:
    {text}

    Please provide the data in the following JSON format. If something is missing respond with "None" for that field:
    {{
        "invoice_number": "<Invoice Number>",
        "invoice_date": "<Invoice Date>",
        "total_amount": "<Total Amount>",
        "vendor_name": "<Vendor Name>"
    }}
    """
    return call_anthropic(prompt, document_type)


def extract_purchase_order_details_with_anthropic(text: str, document_type: str):
    """
    Extract key details for purchase orders using Anthropic's LLM.
    """
    prompt = f"""
    Extract the following details from the purchase order document below:
    1. Purchase Order Number
    2. Order Date
    3. Total Amount
    4. Supplier Name
    
    Document:
    {text}

    Please provide the data in the following JSON format. If something is missing respond with "None" for that field:
    {{
        "Purchase Order Number": "<Purchase Order Number>",
        "Order Date": "<Order Date>",
        "Total Amount": "<Total Amount>",
        "Supplier Name": "<Supplier Name>"
    }}
    """
    
    return call_anthropic(prompt, document_type)



def process_extracted_data(extracted_text: str, document_type: str):
    """
    Process the extracted text into a structured dictionary with key-value pairs.
    """
    # Clean up any unwanted text
    extracted_text = extracted_text.strip()
    print(f"Stripped text: {extracted_text}")
    
    # Try to convert the extracted text into JSON
    extracted_data = {}

    if document_type == "invoice":
    
        try:
            # Manually parse the required fields (invoice_number, invoice_date, etc.)
            invoice_number = re.search(r'"invoice_number":\s*"([^"]*)"', extracted_text)
            invoice_date = re.search(r'"invoice_date":\s*"([^"]*)"', extracted_text)
            total_amount = re.search(r'"total_amount":\s*"([^"]*)"', extracted_text)
            vendor_name = re.search(r'"vendor_name":\s*"([^"]*)"', extracted_text)

            # Assign the values if found, else None
            extracted_data["invoice_number"] = invoice_number.group(1) if invoice_number else None
            extracted_data["invoice_date"] = invoice_date.group(1) if invoice_date else None
            extracted_data["total_amount"] = total_amount.group(1) if total_amount else None
            extracted_data["vendor_name"] = vendor_name.group(1) if vendor_name else None
            
        except Exception as e:
            print(f"Error processing extracted data: {e}")
            return None
        
    elif document_type == "purchase order":
        try:
            # Manually parse the required fields (purchase_order_number, order_date, etc.)
            purchase_order_number = re.search(r'"Purchase Order Number":\s*"([^"]*)"', extracted_text)
            order_date = re.search(r'"Order Date":\s*"([^"]*)"', extracted_text)
            total_amount = re.search(r'"Total Amount":\s*"([^"]*)"', extracted_text)
            supplier_name = re.search(r'"Supplier Name":\s*"([^"]*)"', extracted_text)

            # Assign the values if found, else None
            extracted_data["purchase_order_number"] = purchase_order_number.group(1) if purchase_order_number else None
            extracted_data["order_date"] = order_date.group(1) if order_date else None
            extracted_data["total_amount"] = total_amount.group(1) if total_amount else None
            extracted_data["supplier_name"] = supplier_name.group(1) if supplier_name else None
            
        except Exception as e:
            print(f"Error processing extracted data: {e}")
            return None

    return extracted_data




def call_anthropic(prompt: str, document_type: str):
    """
    Call Anthropic's LLM API to extract details from the document.
    """

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 1000,
        "temperature": 0,
        "system": "You are a document extraction expert.",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        #print(f"Anthropic Full API response: {result}")

        if 'content' in result and isinstance(result['content'], list):
            extracted_text = result['content'][0].get('text', '')
            return process_extracted_data(extracted_text, document_type)

        else:
            print("Error: Invalid response structure")
            return "Error: Invalid response structure"
    
    except requests.exceptions.RequestException as e:
        print(f"Error calling Anthropic API: {e}")
        return None

def extract_data_based_on_type(text: str, document_type: str, email: str, document_name: str):
    """
    Extracts the relevant data from the document based on its type (invoice or purchase order).
    Uses Anthropic LLM for extraction.
    """
    print(f"Document type passed on: {document_type}")
    if document_type == "invoice":
        print(f"Extracting invoice details for {email} from {document_name}")
        extracted_data = extract_invoice_details_with_anthropic(text, document_type)
        extracted_data["email"] = email
        extracted_data["document_name"] = document_name
        print(f"Extracted invoice data sent: {extracted_data}")
        insert_invoice_data(extracted_data)
    elif document_type == "purchase order":
        print(f"Extracting purchase order details for {email} from {document_name}")
        extracted_data = extract_purchase_order_details_with_anthropic(text, document_type)
        extracted_data["email"] = email
        extracted_data["document_name"] = document_name
        print(f"Extracted purchase order data sent: {extracted_data}")
        insert_purchase_order_data(extracted_data)
    else:
        extracted_data = {}

    return extracted_data