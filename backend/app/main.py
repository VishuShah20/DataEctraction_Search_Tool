
'''All of the main improvisations are there along with their routes below and in all the other files:

Would add unit tests if had more time. automate CI/CD like GitHub actions
Would add structured logging (like structlog)
would add request tracing for better observability and debugging.'''
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os
from .models import create_tables
from dotenv import load_dotenv
from app.utils import extract_text_from_pdf
from app.utils import extract_text_from_pdf, extract_data_based_on_type
from app.classifier import classify_document
from app.s3_utils import upload_file_to_s3
from app.s3_utils import get_documents_for_user
from app.database import get_invoices_by_email, get_purchase_orders_by_email
from app.search import search_documents
from app.search import generate_answer
from pydantic import BaseModel
import io  



load_dotenv()

BUCKET_NAME = "gentlyai"

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

'''In production, deploy with multiple FastAPI replicas behind a load balancer. Scale based on rpm and DB connection limits'''
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    email: str



'''For production, would add a queuing system (like Celery or Temporal) to manage ingestion jobs reliably in FCFS manner and retry on failures
Would add a proper auth system like OAuth2 or JWT.'''
@app.post("/upload_document/") 
async def upload_document(
    file: UploadFile = File(...),
    email: str = Form(...)
):
    
    '''Would remove the local path here, and would directly upload to S3 and retrieve docs and texts from there for details extraction as well'''
    try:

        file_content = await file.read()
        # Generate a unique S3 path for the uploaded document
        doc_s3_key = f"documents/{email}_{file.filename}"
        text_s3_key = f"extractedtexts/{email}_{file.filename}.txt"
        
        # Upload the file to S3
        upload_file_to_s3(io.BytesIO(file_content), doc_s3_key)
        
        # Extract the text from the uploaded PDF
        text = extract_text_from_pdf(io.BytesIO(file_content))
        
        # Upload the extracted text to S3
        text_file = io.BytesIO(text.encode('utf-8'))
        upload_file_to_s3(text_file, text_s3_key)

        # Classify the document
        doc_type = classify_document(text)
        
        # Extract the necessary data based on the document type
        extracted_data = extract_data_based_on_type(text, doc_type, email, file.filename)
        
        # Return the document URL and extracted data
        return {
            "message": "Uploaded and processed successfully.",
            "document_type": doc_type,
            "document_url": f"s3://{BUCKET_NAME}/{doc_s3_key}",
            "extracted_text_url": f"s3://{BUCKET_NAME}/{text_s3_key}",
            "extracted_data": extracted_data  
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
'''Would add flexible doc search using DocType and DocParams as a dict to allow specific retrievals'''
@app.get("/documents")
async def get_documents(email: str):
    
    #Fetch all documents uploaded by the user (based on email ID).

    try:
        # get all documents for the user from S3(based on email ID)
        documents = get_documents_for_user(email)
        
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found for this user.")
        
        return {"documents": documents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
'''Would let user search by document type and other params as well, also would allow querying'''
@app.get("/get_key_details")
async def get_key_details(email: str):
    
    #Fetch all documents (invoices and purchase orders) associated with the user's email from PostgreSQL.

    try:
        # Fetch all invoices and purchase orders for the user from PostgreSQL
        invoices = get_invoices_by_email(email)
        purchase_orders = get_purchase_orders_by_email(email)

        if not invoices and not purchase_orders:
            raise HTTPException(status_code=404, detail="No documents found for this email.")

        # combine both invoices and purchase orders
        document_details = {
            "invoices": invoices,
            "purchase_orders": purchase_orders
        }

        return document_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


'''For production, would ensure server can scale (multiple replicas using Kubernetes)
Math: max_parallel_requests = total_allowed_db_connections / connections_per_request
Claude API limits and DB throughput should be considered when load testing'''

''' For scaling search, consider OpenSearch with indexing and a reranker. For highest accuracy, a full RAG pipeline could be used (higher infra cost)'''
@app.post("/search_answer/")
async def search_answer(payload: SearchRequest):
    try:
        query = payload.query
        email = payload.email

        #fuzzy search
        search_results = search_documents(query, email)

        if not search_results:
            raise HTTPException(status_code=404, detail="No relevant documents found for this query.")
        
        print(f"[DEBUG] Found {len(search_results)} relevant documents.")

        
        #Extract text
        relevant_text = " ".join([result["relevant_text"] for result in search_results])

        # Generate answer
        answer = generate_answer(relevant_text, query, search_results)

        if not answer:
            raise HTTPException(status_code=500, detail="Error generating an answer.")

        return {
            "answer": answer,
            "source_documents": [result["document_name"] for result in search_results]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    



@app.get("/")
def read_root():
    return {"message": "Welcome to the Data Extraction API"}