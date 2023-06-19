import React, { useState } from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import { Navigate, BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages";
import KnowledgeDailyDigest from "./pages/knowledgedailydigest";
import ArtOfTheDay from "./pages/artoftheday";
import KnowledgeQuery from "./pages/knowledgequery";
import GoogleLoginButton from './pages/googleloginpage';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" exact element={<Home />} />
        <Route path="/artoftheday" element={<ArtOfTheDay />} />
        <Route path="/knowledgequery" element={<KnowledgeQuery />} />
        <Route path="/googleloginpage">
          <GoogleLoginButton setIsAuthenticated={setIsAuthenticated} />
        </Route>
        <Route path="/protected">
          {isAuthenticated ? (
            <KnowledgeDailyDigest />
          ) : (
            <Navigate to="/googleloginpage" />
          )}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
