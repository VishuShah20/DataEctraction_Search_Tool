
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const DocumentDetails: React.FC = () => {
    const { documentId } = useParams(); 
    const [documentDetails, setDocumentDetails] = useState<any>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        if (documentId) {
            fetchDocumentDetails(documentId);
        }
    }, [documentId]);

    const fetchDocumentDetails = async (documentId: string) => {
        setLoading(true);
        setError('');
        try {
            const response = await fetch(`http://localhost:8000/document_details/${documentId}?email=user@example.com`); //pass email dynamically
            const data = await response.json();
            if (response.ok) {
                setDocumentDetails(data);
            } else {
                setError("No document found.");
            }
        } catch (error) {
            setError("Error fetching document details.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h3>Document Details</h3>
            {loading && <p>Loading...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {documentDetails && (
                <div>
                    <h4>Document Type: {documentDetails.invoice ? "Invoice" : "Purchase Order"}</h4>
                    {documentDetails.invoice && (
                        <div>
                            <h5>Invoice Details</h5>
                            <p>Invoice Number: {documentDetails.invoice.invoice_number}</p>
                            <p>Invoice Date: {documentDetails.invoice.invoice_date}</p>
                            <p>Total Amount: {documentDetails.invoice.total_amount}</p>
                            <p>Vendor: {documentDetails.invoice.vendor_name}</p>
                        </div>
                    )}
                    {documentDetails.purchase_order && (
                        <div>
                            <h5>Purchase Order Details</h5>
                            <p>Order Number: {documentDetails.purchase_order.purchase_order_number}</p>
                            <p>Order Date: {documentDetails.purchase_order.order_date}</p>
                            <p>Total Amount: {documentDetails.purchase_order.total_amount}</p>
                            <p>Supplier: {documentDetails.purchase_order.supplier_name}</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default DocumentDetails;