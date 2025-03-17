import React, { useState,useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './components/dashboard/Dashboard';
import BotIntegrationPage from './components/integration/BotIntegrationPage';
import ContributorsPage from './components/contributors/ContributorsPage';
import PullRequestsPage from './components/pages/PullRequestsPage';
import SettingsPage from './components/pages/SettingsPage';
import AnalyticsPage from './components/pages/AnalyticsPage';
import SupportPage from './components/pages/SupportPage';
import LandingPage from './components/landing/LandingPage';
import LoginPage from './components/pages/LoginPage';
import ProfilePage from './components/pages/ProfilePage';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activePage, setActivePage] = useState('landing'); // Default to landing page
  const [repoData, setRepoData] = useState<any>(null); // Store fetched repo stats
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const user = localStorage.getItem('isAuthenticated');
    if (user === 'true') {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
    localStorage.setItem('isAuthenticated', 'true'); 
  };

  // Function to handle logout
  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('isAuthenticated'); 
  };
  const renderPage = () => {
    switch (activePage) {
      case 'landing':
        return <LandingPage setRepoData={setRepoData} setActivePage={setActivePage} />;
      case 'dashboard':
        return <Dashboard repoData={repoData} />;
      case 'integration':
        return <BotIntegrationPage />;
      case 'contributors':
        return <ContributorsPage repoData={repoData} />;
      case 'analytics':
        return <AnalyticsPage repoData={repoData} />;
      case 'prs':
        return <PullRequestsPage repoData={repoData} />;
      case 'support':
        return <SupportPage />;
      case 'settings':
        return <SettingsPage />;
      case 'profile':
        return <ProfilePage />;
      default:
        return <Dashboard repoData={repoData} />;
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-950 text-white">
        <Routes>
          {/* If not logged in, redirect all routes to login */}
          <Route
            path="/login"
            element={<LoginPage />}
          />
          <Route
            path="/"
            element={
                <>
                  <Sidebar
                    isOpen={isSidebarOpen}
                    setIsOpen={setIsSidebarOpen}
                    activePage={activePage}
                    setActivePage={setActivePage}
                  />
                  <main className={`transition-all duration-300 ${isSidebarOpen ? 'ml-64' : 'ml-20'}`}>
                    <div className="p-8">
                      <AnimatePresence mode="wait">{renderPage()}</AnimatePresence>
                    </div>
                  </main>
                </>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
