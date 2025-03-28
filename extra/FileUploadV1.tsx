import React, { useState } from 'react';

const FileUpload: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [documentType, setDocumentType] = useState<string | null>(null);
    const [emailInput, setEmailInput] = useState<string>(''); // Track email input
    const [emailSubmitted, setEmailSubmitted] = useState<boolean>(false); // Track email submission status
    const [emailError, setEmailError] = useState<string>(''); // Track any email errors
    const [documents, setDocuments] = useState<any[]>([]); // Track documents
    const [documentDetails, setDocumentDetails] = useState<any>(null); // Track document details
    const [loadingDetails, setLoadingDetails] = useState<boolean>(false); // Loading state for details

    const handleEmailSubmit = (e: React.FormEvent) => {
        e.preventDefault(); // Prevent the default form submission
        if (!emailInput || !/\S+@\S+\.\S+/.test(emailInput)) {
            setEmailError("Please enter a valid email.");
            return;
        }
        setEmailSubmitted(true); // Set email as submitted
        setEmailError(''); // Reset email error
        fetchDocuments(emailInput); // Fetch documents when email is submitted
    };

    // Fetch documents for the user based on email
    const fetchDocuments = async (email: string) => {
        try {
            const response = await fetch(`http://localhost:8000/documents?email=${email}`);
            const data = await response.json();
            if (response.ok) {
                setDocuments(data.documents);
            } else {
                alert("No documents found.");
            }
        } catch (error) {
            console.error("Error fetching documents", error);
            alert("Error fetching documents.");
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return alert("Please select a file first.");
        if (!emailInput) return alert("Please submit your email first.");

        const formData = new FormData();
        formData.append("file", file);
        formData.append("email", emailInput);

        try {
            const response = await fetch("http://localhost:8000/upload_document/", {
                method: "POST",
                body: formData,
            });
            const data = await response.json();
            setDocumentType(data.document_type);
            alert("File uploaded successfully!");
        } catch (error) {
            console.error(error);
            alert("Error uploading file.");
        }
    };

    // Fetch document details based on document ID (independently of download)
    const fetchDocumentDetails = async () => {
        setLoadingDetails(true);
        try {
            const response = await fetch(`http://localhost:8000/get_key_details?email=${emailInput}`);
            const data = await response.json();
            if (response.ok) {
                setDocumentDetails(data);
            } else {
                setDocumentDetails(null);
                alert("No document details found.");
            }
        } catch (error) {
            setDocumentDetails(null);
            alert("Error fetching document details.");
        } finally {
            setLoadingDetails(false);
        }
    };

    return (
        <div>
            {!emailSubmitted ? (
                <form onSubmit={handleEmailSubmit}>
                    <input
                        type="email"
                        placeholder="Enter your email"
                        value={emailInput}
                        onChange={(e) => setEmailInput(e.target.value)}
                    />
                    <button type="submit">Submit Email</button>
                    {emailError && <p style={{ color: 'red' }}>{emailError}</p>}
                </form>
            ) : (
                <div>
                    <p>Using email: <strong>{emailInput}</strong></p>
                    <input type="file" accept=".pdf" onChange={handleFileChange} />
                    <button onClick={handleUpload}>Upload PDF</button>
                    {documentType && <p>Document Type: {documentType}</p>}

                    {/* Display documents if there are any */}
                    {documents.length > 0 && (
                        <div>
                            <h3>Your Documents</h3>
                            <ul>
                                {documents.map((doc, index) => (
                                    <li key={index}>
                                        {/* Link to download the document from S3 */}
                                        <a href={`https://s3.amazonaws.com/gentlyai/${doc.document_url}`} target="_blank" rel="noopener noreferrer">
                                            {doc.document_name}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <button onClick={fetchDocumentDetails}>Get Key Detail</button>

                    {/* Display document details if available */}
                    {documentDetails && (
                        <div>
                            <h3>Key Document Details</h3>
                            {documentDetails.invoices && (
                                <div>
                                    <h4>Invoices:</h4>
                                    <ul>
                                        {documentDetails.invoices.map((invoice: any, index: number) => (
                                            <li key={index}>
                                                <p>Invoice Number: {invoice.invoice_number}</p>
                                                <p>Total Amount: {invoice.total_amount}</p>
                                                <p>Invoice Date: {invoice.invoice_date}</p>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                            {documentDetails.purchase_orders && (
                                <div>
                                    <h4>Purchase Orders:</h4>
                                    <ul>
                                        {documentDetails.purchase_orders.map((order: any, index: number) => (
                                            <li key={index}>
                                                <p>Order Number: {order.purchase_order_number}</p>
                                                <p>Supplier: {order.supplier_name}</p>
                                                <p>Total Amount: {order.total_amount}</p>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}

                    {loadingDetails && <p>Loading document details...</p>}
                </div>
            )}
        </div>
    );
};

export default FileUpload;