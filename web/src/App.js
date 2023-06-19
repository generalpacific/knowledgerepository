import React, { useState } from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import PrivateRoute from './PrivateRoute';
import Home from "./pages";
import KnowledgeDailyDigest from "./pages/knowledgedailydigest";
import ArtOfTheDay from "./pages/artoftheday";
import KnowledgeQuery from "./pages/knowledgequery";
import GoogleLoginButton from './pages/googleloginpage';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
  };

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
          <Route path="/googleloginpage">
            <GoogleLoginButton setIsAuthenticated={setIsAuthenticated} />
          </Route>
          <PrivateRoute path="/knowledgedailydigest" component={KnowledgeDailyDigest} isAuthenticated={isAuthenticated}/>
      </Routes>
    </Router>
  );
}

export default App;
