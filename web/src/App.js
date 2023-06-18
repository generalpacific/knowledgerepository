import React from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages";
import KnowledgeDailyDigest from "./pages/knowledgedailydigest";
import ArtOfTheDay from "./pages/artoftheday";
import KnowledgeQuery from "./pages/knowledgequery";
import GoogleLoginButton from './pages/googleloginpage';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" exact element={<Home />} />
        <Route
          path="/knowledgedailydigest"
          element={<KnowledgeDailyDigest />}
        />
        <Route path="/artoftheday" element={<ArtOfTheDay />} />
        <Route path="/knowledgequery" element={<KnowledgeQuery />} />
        <Route path="/googleloginpage" element={<GoogleLoginButton />} />
      </Routes>
    </Router>
  );
}

export default App;
