'''Would use a managed DB (like AWS RDS) with auto scaling for high traffic'''
'''Have used two seperate tables for for invoices and purchase orders that would give
better read speed, strong typing, and reduces edge case handling in extraction, but is costlier.
Could implement union schema for flexibility if required

Would use Pydantic model instead of raw dict parsing'''
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime
import time
from urllib.parse import urlparse


load_dotenv()

'''DB_HOST = os.getenv("DB_HOST")
print("DB_HOST:", DB_HOST)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")'''
DATABASE_URL = os.getenv("DATABASE_URL")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


'''def connect_db():
    retries = 5
    for i in range(retries):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            return conn
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            time.sleep(10)  # wait for 5 seconds before retrying
    return None'''

def connect_db():
    retries = 5
    for i in range(retries):
        try:
            # Parsing the DATABASE_URL and establishing the connection
            result = urlparse(DATABASE_URL)
            print(f"Connecting to DB at {result.hostname}:{result.port} with database {result.path[1:]}")
            conn = psycopg2.connect(
                host=result.hostname,
                port=result.port,
                database=result.path[1:], 
                user=result.username,
                password=result.password
            )
            return conn
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            time.sleep(3)  
    return None

#insert data into the invoices table
def insert_invoice_data(data: dict):
    conn = connect_db()
    if conn is None:
        print("Error: Unable to connect to the database")
        return
    cursor = conn.cursor()

    try:
        # mapping the extracted data to the corresponding DB columns
        user_email = data.get("email")
        document_name = data.get("document_name")
        invoice_number = data.get("invoice_number")  
        invoice_date = data.get("invoice_date")  
        total_amount = data.get("total_amount")  
        vendor_name = data.get("vendor_name")  

        print("Data to be inserted into invoices:")
        print(f"Email: {user_email}")
        print(f"Document Name: {document_name}")
        print(f"Invoice Number: {invoice_number}")
        print(f"Invoice Date: {invoice_date}")
        print(f"Total Amount: {total_amount}")
        print(f"Vendor Name: {vendor_name}")

        #execute insert query
        cursor.execute("""
            INSERT INTO invoices (user_email, document_name, invoice_number, date, total_amount, vendor_name, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_email, document_name, invoice_number, invoice_date, total_amount, vendor_name, datetime.now()))

        conn.commit()
        print(f" All the data inserted: ", user_email, document_name, invoice_number, invoice_date, total_amount, vendor_name)

    except Exception as e:
        # More detailed debugging: log the error
        print(f"Error inserting invoice data: {e}")
        print(f"Full traceback: {e.__traceback__}")

        #Check
        if "email" in str(e).lower():
            print("The issue might be with the 'email'")
        elif "total_amount" in str(e).lower():
            print("The issue might be with the 'total_amount' field.")
        else:
            print("Other error occurred.")

    finally:
        cursor.close()
        conn.close()

def insert_purchase_order_data(data: dict):
    conn = connect_db()
    if conn is None:
        print("Error: Unable to connect to the database")
        return
    cursor = conn.cursor()

    try:
        user_email = data.get("email")
        document_name = data.get("document_name")
        purchase_order_number = data.get("purchase_order_number") 
        order_date = data.get("order_date")  
        total_amount = data.get("total_amount")  
        supplier_name = data.get("supplier_name") 

        print("Data to be inserted into purchase_orders:")
        print(f"Email: {user_email}")
        print(f"Document Name: {document_name}")
        print(f"Purchase Order Number: {purchase_order_number}")
        print(f"Order Date: {order_date}")
        print(f"Total Amount: {total_amount}")
        print(f"Supplier Name: {supplier_name}")

        cursor.execute("""
            INSERT INTO purchase_orders (user_email, document_name, purchase_order_number, order_date, total_amount, supplier_name, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_email, document_name, purchase_order_number, order_date, total_amount, supplier_name, datetime.now()))

        conn.commit()
        print(f" Purchase order data inserted for {user_email}")

    except Exception as e:
        #detailed Debugging
        print(f" Error inserting purchase order data: {e}")
        print(f"Full traceback: {e.__traceback__}")

        if "email" in str(e).lower():
            print("The issue might be with the 'email'")
        elif "total_amount" in str(e).lower():
            print("The issue might be with the 'total_amount' field")
        else:
            print("Other error occurred")

    finally:
        cursor.close()
        conn.close()


def get_invoice_by_document(document_name: str, email: str):
    
    #Fetch invoice details by document name (or any identifier) and user email.
    
    conn = connect_db()
    if conn is None:
        print("Error: Unable to connect to the database")
        return None
    cursor = conn.cursor()

    try:
        # query the invoices table for the given document name and email
        cursor.execute("""
            SELECT * FROM invoices WHERE document_name = %s AND user_email = %s
        """, (document_name, email))

        invoice = cursor.fetchone()
        print(f"Fetched invoice: {invoice}")

        if not invoice:
            return None

        #return data as a dictionary
        invoice_data = {
            "invoice_number": invoice[7], 
            "invoice_date": invoice[2],
            "total_amount": invoice[4],
            "vendor_name": invoice[4]
        }

        return invoice_data

    except Exception as e:
        print(f"Error fetching invoice data: {e}")
        return None

    finally:
        cursor.close()
        conn.close()


# Fetch invoices by email
def get_invoices_by_email(email: str):
    
    #Fetch all invoices associated with the user's email.
    
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM invoices WHERE user_email = %s
        """, (email,))
        
        invoices = cursor.fetchall()
        print(f"Fetched invoices: {invoices}") 
        invoice_data = []
        for invoice in invoices:
            invoice_data.append({
                "invoice_number": invoice[7], 
                "invoice_date": invoice[2],
                "total_amount": invoice[4],
                "vendor_name": invoice[4]
            })

        print(f"Invoice data: {invoice_data}")

        return invoice_data

    except Exception as e:
        print(f"Error fetching invoices: {e}")
        return []

    finally:
        cursor.close()
        conn.close()

# Fetch purchase orders by email
def get_purchase_orders_by_email(email: str):
    
    #Fetch all purchase orders associated with the user's email.
    
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM purchase_orders WHERE user_email = %s
        """, (email,))
        
        purchase_orders = cursor.fetchall()
        purchase_order_data = []
        for order in purchase_orders:
            purchase_order_data.append({
                "purchase_order_name": order[2],
                "order_date": order[4],
                "total_amount": order[5],
                "supplier_name": order[6]
            })

        print(f"Purchase order data: {purchase_order_data}")

        return purchase_order_data

    except Exception as e:
        print(f"Error fetching purchase orders: {e}")
        return []

    finally:
        cursor.close()
        conn.close()