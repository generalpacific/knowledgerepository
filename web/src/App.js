import React, { useState } from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages";
import KnowledgeDailyDigest from "./pages/knowledgedailydigest";
import Chat from "./pages/chat";
import ArtOfTheDay from "./pages/artoftheday";
import KnowledgeQuery from "./pages/knowledgequery";
import GoogleLoginButton from './pages/googleloginpage';
import RandomEntity from './pages/randomentity';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" exact element={<Home />} />
        <Route path="/artoftheday" element={<ArtOfTheDay />} />
        <Route path="/knowledgequery" element={<KnowledgeQuery />} />
        <Route path="/googleloginpage" element={<GoogleLoginButton setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="/knowledgedailydigest" element={<KnowledgeDailyDigest isAuthenticated={true}/>} />
        <Route path="/chat" element={<Chat isAuthenticated={isAuthenticated}/>} />
        <Route path="/randomentity" element={<RandomEntity />} />
      </Routes>
    </Router>
  );
}

export default App;
