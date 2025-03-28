import React from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import FileUpload from './components/FileUpload';
import DocumentDetails from './components/DocumentDetails';

const App: React.FC = () => {
  return (
    <div className="App">
      <Router>
        <div className="page-container">
          <h1>Document Management System</h1>
          <Routes>
            <Route path="/" element={<FileUpload />} />
            <Route path="/document_details/:documentId" element={<DocumentDetails />} />
          </Routes>
        </div>
      </Router>
    </div>
  );
};

export default App;