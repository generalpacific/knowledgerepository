import React from 'react';
import './App.css';
import Navbar from './components/Navbar';
import { BrowserRouter as Router, Routes, Route}
    from 'react-router-dom';
import Home from './pages';
import KnowledgeDailyDigest from './pages/knowledgedailydigest';
  
function App() {
return (
    <Router>
    <Navbar />
    <Routes>
        <Route exact path='/' exact element={<Home />} />
        <Route path='/knowledgedailydigest' element={<KnowledgeDailyDigest />} />
    </Routes>
    </Router>
);
}
  
export default App;
