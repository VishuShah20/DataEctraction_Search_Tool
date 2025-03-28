from sqlalchemy import create_engine, Column, Integer, String, Date, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")  #postgres://user:password@localhost/dbname


Base = declarative_base()

class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP, nullable=False)
    date = Column(Date, nullable=False)
    invoice_number = Column(String, nullable=False)
    vendor_name = Column(String, nullable=False)
    total_amount = Column(Text, nullable=False)
    user_email = Column(String, nullable=False)
    document_name = Column(String, nullable=False)


class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP, nullable=False)
    order_date = Column(Date, nullable=False)
    purchase_order_number = Column(String, nullable=False)
    supplier_name = Column(String, nullable=False)
    total_amount = Column(Text, nullable=False)
    user_email = Column(String, nullable=False)
    document_name = Column(String, nullable=False)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)