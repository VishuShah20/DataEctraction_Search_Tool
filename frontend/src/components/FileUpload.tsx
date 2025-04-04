import React, { useState } from 'react';
import ChatBot from './ChatBot';

const FileUpload: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [documentType, setDocumentType] = useState<string | null>(null);
    const [emailInput, setEmailInput] = useState<string>(''); //Track email input
    const [emailSubmitted, setEmailSubmitted] = useState<boolean>(false); //Track email submission status
    const [emailError, setEmailError] = useState<string>(''); //Track any email errors
    const [documents, setDocuments] = useState<any[]>([]); //track documents
    const [documentDetails, setDocumentDetails] = useState<any>(null); // track document details
    const [loadingDetails, setLoadingDetails] = useState<boolean>(false); //Loading state for details
    const [uploading, setUploading] = useState<boolean>(false);
    const [isProcessing, setIsProcessing] = useState<boolean>(false);

    const handleEmailSubmit = (e: React.FormEvent) => {
        e.preventDefault(); // Prevent default form submission
        if (!emailInput || !/\S+@\S+\.\S+/.test(emailInput)) {
            setEmailError("Please enter a valid email.");
            return;
        }
        setEmailSubmitted(true); 
        setEmailError(''); 
        fetchDocuments(emailInput);
    };

    // fetch documents for the user based on email
    const fetchDocuments = async (email: string) => {
        try {
            const response = await fetch(`http://localhost:8000/documents?email=${email}`);
            const data = await response.json();
            console.log("Fetched Documents:", data);
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

        setUploading(true);
        setIsProcessing(true);

        const formData = new FormData();
        formData.append("file", file);
        formData.append("email", emailInput);
        console.log("Uploading file with email:", emailInput, "File:", file);

        console.log("Uploading email:", emailInput, file);

        try {
            const response = await fetch("http://localhost:8000/upload_document/", {
                method: "POST",
                body: formData,
            });
            console.log("Response:", response);
            const data = await response.json();
            setDocumentType(data.document_type);
            setIsProcessing(false);
            //alert("File uploaded successfully!");
            fetchDocuments(emailInput);
        } catch (error) {
            console.error(error);
            alert("Error uploading file.");
        } finally {
            setUploading(false);
        }
    };

    const uploadButtonDisabled = isProcessing;

    // fetch document details based on document ID (independently of download)
    const fetchDocumentDetails = async () => {
        setLoadingDetails(true);
        try {
            const response = await fetch(`http://localhost:8000/get_key_details?email=${emailInput}`);
            const data = await response.json();
            
            console.log("Fetched Document Details:", data);
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

                    <button onClick=
                    {handleUpload}
                    disabled={uploadButtonDisabled}
                    className={uploadButtonDisabled ? "disabled-button" : ""}>
                        Upload PDF</button>

                    {uploading && <div className="spinner"></div>}
                    {documentType && <p>Document Type: {documentType}</p>}

                    {/*dsplay docs if aany*/}
                    {documents.length > 0 && (
                        <div>
                            <h3>Your Documents</h3>
                            <ul>
                                {documents.map((doc, index) => (
                                    <li key={index}>
                                        {/* Link to download the doc*/}
                                        <a href={doc.document_url} target="_blank" rel="noopener noreferrer">
                                            {doc.document_name}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <button onClick={fetchDocumentDetails}>Get Key Detail</button>

                    {}
                    {documentDetails && (
                        <div>
                            <h3>Key Document Details</h3>
                            {console.log("Document Details to display:", documentDetails)}

                            {}
                            {documentDetails.invoices && (
                                <div>
                                    <h4>Invoices:</h4>
                                    <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                                        <thead>
                                            <tr>
                                                <th style={{ border: '1px solid black', padding: '8px' }}>Invoice Name</th>
                                                <th style={{ border: '1px solid black', padding: '8px' }}>Invoice Date</th>
                                                <th style={{ border: '1px solid black', padding: '8px' }}>Total amount</th>
                                                <th style={{ border: '1px solid black', padding: '8px' }}>Vendor Name</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {documentDetails.invoices.map((invoice: any, index: number) => (
                                                <tr key={index}>
                                                    <td style={{ border: '1px solid black', padding: '8px' }}>{invoice.invoice_name}</td>
                                                    <td style={{ border: '1px solid black', padding: '8px' }}>{invoice.invoice_date}</td>
                                                    <td style={{ border: '1px solid black', padding: '8px' }}>{invoice.total_amount}</td>
                                                    <td style={{ border: '1px solid black', padding: '8px' }}>{invoice.vendor_name}</td>
                                                </tr>
                                            ))}
                                            
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            {}
                            {documentDetails.purchase_orders && (
                                <div>
                                    <h4>Purchase Orders:</h4>
                                    <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                                        <thead>
                                            <tr>
                                                <th style={{ border: '1px solid black', padding: '8px' }}>Order Name</th>
                                                <th style={{ border: '1px solid black', padding: '8px' }}>Order Date</th>
                                                <th style={{ border: '1px solid black', padding: '8px' }}>Total Amount</th>
                                                <th style={{ border: '1px solid black', padding: '8px' }}>Supplier Name</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {documentDetails.purchase_orders.map((order: any, index: number) => (
                                                <tr key={index}>
                                                    <td style={{ border: '1px solid black', padding: '8px' }}>{order.purchase_order_name}</td>
                                                    <td style={{ border: '1px solid black', padding: '8px' }}>{order.order_date}</td>
                                                    <td style={{ border: '1px solid black', padding: '8px' }}>{order.total_amount}</td>
                                                    <td style={{ border: '1px solid black', padding: '8px' }}>{order.supplier_name}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}

                    {loadingDetails && <p>Loading document details...</p>}
                </div>
            )}

            {emailSubmitted && (
            <div>
                

                <h3>Ask a Question</h3>
                <ChatBot email={emailInput} />
            </div>
            )}
        </div>
    );
};

export default FileUpload;