'''
Using blocking I/O (boto3/psycopg2) currently, would move to ioboto3 and asyncpg to allow concurrent async requests
Would cache S3 object listing using in-memory cache or index keys in Postgresql to reduce response time and cost

code improvements:
Would improve naming convention. like documents/{email}/{filename}.pdf to avoid collisions 
and parallel uploads'''
import boto3
import os

AWS_REGION = "us-east-2"  
BUCKET_NAME = "gentlyai"  
EXTRACTED_TEXTS_FOLDER = "extractedtexts/"

#initialize the S3 client(bucket has public access)
s3_client = boto3.client("s3", region_name=AWS_REGION)

def upload_file_to_s3(file_path: str, email: str, file_type: str):
    
    #Upload a file to S3. Email is used as a prefix in the filename, not as a folder. file_type is either "documents" or "extractedtexts".
    
    original_filename = os.path.basename(file_path)
    s3_key = f"{file_type}/{email}_{original_filename}"
    print(f"Uploading to S3: {s3_key}") 

    try:
        with open(file_path, "rb") as file_data:
            s3_client.upload_fileobj(file_data, BUCKET_NAME, s3_key)
            print(f"Uploaded {file_path} to s3://{BUCKET_NAME}/{s3_key}")
            return s3_key
    except Exception as e:
        print(f" Error uploading file: {e}")
        raise e

def upload_document_and_text(document_path: str, extracted_text: str):
    """
    uploads the original document and its extracted text (as a .txt file) to S3.
    Returns the S3 keys for both uploads.
    """
    #generate unique filenames to avoid collisions
    doc_filename = document_path
    text_filename = document_path + ".txt"
    
    #Define S3 paths (folder structure inside the bucket)
    s3_doc_path = f"documents/{doc_filename}"
    s3_text_path = f"extractedtexts/{text_filename}"
    
    # Upload the document
    upload_file_to_s3(document_path, s3_doc_path)
    
    #Create a temporary text file
    text_file_path = document_path + ".txt"
    with open(text_file_path, "w") as f:
        f.write(extracted_text)
    # Upload the extracted text file
    upload_file_to_s3(text_file_path, s3_text_path)
    
    return s3_doc_path, s3_text_path

def get_documents_for_user(email: str):
    
    #Fetch the list of documents stored in the S3 bucket for the user. Uses email as a prefix to search documents in the S3 'documents' folder.
    try:
        # List all docs with email prefix
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f"documents/{email}_")

        if 'Contents' not in response:
            return []

        # extract doc names and urls
        documents = []
        for obj in response['Contents']:
            s3_key = obj['Key']
            document_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
            documents.append({
                "document_name": s3_key,
                "document_url": document_url
            })

        return documents
    except Exception as e:
        print(f"Error fetching documents from S3: {e}")
        return []
    

def get_s3_documents(email: str):
    prefix = f"{EXTRACTED_TEXTS_FOLDER}{email}_"
    print(f"\n S3 Search Prefix: {prefix}")
    
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    print(f"Raw S3 Response: {response}")

    if "Contents" not in response:
        return []

    document_names = [obj["Key"].split("/")[-1] for obj in response["Contents"]]
    print(f"Matched Documents: {document_names}")
    return document_names


def get_s3_file_content(file_key: str):
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
        content = response["Body"].read().decode("utf-8")
        return content
    except Exception as e:
        print(f"Error fetching file content: {e}")
        return ""