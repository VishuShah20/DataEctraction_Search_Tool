import React, { useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import FileUpload from './components/FileUpload'; 
import DocumentDetails from './components/DocumentDetails';  // Import DocumentDetails component

const App: React.FC = () => {
    return (
        <div className="App">
            <h1>Document Management System</h1>
            <Router>
                <Routes>
                    <Route path="/" element={<FileUpload />} />
                    <Route path="/document_details/:documentId" element={<DocumentDetails />} /> {/* Add route for document details */}
                </Routes>
            </Router>
        </div>
    );
}

export default App;