import os
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from faker import Faker

# Initialize Faker to generate random data
fake = Faker()

# Folder paths
base_path = "/Users/vishu/Documents/Documents_example"
contract_path = os.path.join(base_path, "Contract")
invoice_path = os.path.join(base_path, "Invoice")
purchase_order_path = os.path.join(base_path, "PurchaseOrder")

# Ensure folders exist
os.makedirs(contract_path, exist_ok=True)
os.makedirs(invoice_path, exist_ok=True)
os.makedirs(purchase_order_path, exist_ok=True)

def generate_contract(path, idx):
    filename = f"contract_{idx+1}.pdf"
    c = canvas.Canvas(os.path.join(path, filename), pagesize=letter)

    # Adding contract content
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"Contract Agreement: {fake.uuid4()}")
    c.setFont("Helvetica", 12)
    c.drawString(100, 735, f"Date: {fake.date()}")
    c.drawString(100, 720, f"Parties: {fake.company()} and {fake.company()}")
    c.drawString(100, 705, f"Agreement Terms: {fake.bs()}")
    c.drawString(100, 690, f"Contract Amount: ${random.randint(1000, 5000)}")
    c.drawString(100, 675, f"Signatories: {fake.name()} and {fake.name()}")

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(100, 50, f"Terms: This contract is legally binding for both parties.")

    c.save()

def generate_invoice(path, idx):
    filename = f"invoice_{idx+1}.pdf"
    c = canvas.Canvas(os.path.join(path, filename), pagesize=letter)

    # Adding invoice content
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"Invoice: {fake.uuid4()}")
    c.setFont("Helvetica", 12)
    c.drawString(100, 735, f"Invoice Date: {fake.date()}")
    c.drawString(100, 720, f"Billing To: {fake.name()}")
    c.drawString(100, 705, f"Amount Due: ${random.randint(100, 1000)}")
    c.drawString(100, 690, f"Invoice Number: {fake.uuid4()}")
    c.drawString(100, 675, f"Payment Terms: Due in 30 days")

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(100, 50, f"Please remit payment by {fake.date()}. Thank you!")

    c.save()

def generate_purchase_order(path, idx):
    filename = f"purchase_order_{idx+1}.pdf"
    c = canvas.Canvas(os.path.join(path, filename), pagesize=letter)

    # Adding purchase order content
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"Purchase Order: {fake.uuid4()}")
    c.setFont("Helvetica", 12)
    c.drawString(100, 735, f"PO Date: {fake.date()}")
    c.drawString(100, 720, f"Ordered By: {fake.company()}")
    c.drawString(100, 705, f"Items Ordered: {random.randint(1, 5)} items")
    c.drawString(100, 690, f"Total Amount: ${random.randint(500, 5000)}")
    c.drawString(100, 675, f"Payment Method: Wire Transfer")

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(100, 50, f"Shipping Terms: Standard delivery. Contact us for expedited service.")

    c.save()

# Generate 25 documents for each type and store them in their respective directories
for idx in range(25):
    generate_contract(contract_path, idx)
    generate_invoice(invoice_path, idx)
    generate_purchase_order(purchase_order_path, idx)

print("25 Contracts, 25 Invoices, and 25 Purchase Orders have been generated successfully!")