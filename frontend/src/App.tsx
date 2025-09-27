import React, { useEffect, useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import About from './components/About';
import Navbar from './components/Navbar';

function App() {
  const [apiStatus, setApiStatus] = useState<string>('checking...');

  useEffect(() => {
    // Check API connection
    fetch('/api/v1/health/')
      .then(response => response.json())
      .then(data => setApiStatus(data.status))
      .catch(() => setApiStatus('disconnected'));
  }, []);

  return (
    <Router>
      <div className="App">
        <Navbar />
        <header className="App-header">
          <h1>Welcome to Wizbi</h1>
          <p>API Status: {apiStatus}</p>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;