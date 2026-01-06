import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';

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
import SignUpPage from './components/pages/SignUpPage';
import ForgotPasswordPage from './components/pages/ForgotPasswordPage';
import ResetPasswordPage from './components/pages/ResetPasswordPage';
import { useAuth } from './hooks/useAuth';
import { RepositoryData } from './types';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [repoData, setRepoData] = useState<RepositoryData | null>(null);
  const { isAuthenticated, loading, logout } = useAuth();

  if (loading) {
    return <div className="min-h-screen bg-gray-950 flex items-center justify-center text-white">Loading...</div>;
  }

  const handleLogin = () => {
    // Auth state is handled by the useAuth hook listener
  };

  const handleLogout = async () => {
    await logout();
  };

  const ProtectedLayout = () => (
    <div className="flex">
      <Sidebar
        isOpen={isSidebarOpen}
        setIsOpen={setIsSidebarOpen}
        onLogout={handleLogout}
      />
      <main
        className={`transition-all duration-300 flex-1 ${isSidebarOpen ? 'ml-64' : 'ml-20'
          }`}
      >
        <div className="p-8">
          <AnimatePresence mode="wait">
            <Outlet />
          </AnimatePresence>
        </div>
      </main>
    </div>
  );

  return (
    <Router>
      <div className="min-h-screen bg-gray-950 text-white">
        <Toaster position="top-right" />
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated ? (
                <Navigate to="/" replace />
              ) : (
                <LoginPage onLogin={handleLogin} />
              )
            }
          />
          <Route
            path="/forgot-password"
            element={
              isAuthenticated ? (
                <Navigate to="/" replace />
              ) : (
                <ForgotPasswordPage />
              )
            }
          />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route
            path="/signup"
            element={
              isAuthenticated ? <Navigate to="/" replace /> : <SignUpPage />
            }
          />
          <Route
            path="/"
            element={
              isAuthenticated ? <ProtectedLayout /> : <Navigate to="/login" replace />
            }
          >
            <Route index element={<LandingPage setRepoData={setRepoData} />} />
            <Route path="dashboard" element={<Dashboard repoData={repoData} />} />
            <Route path="integration" element={<BotIntegrationPage />} />
            <Route path="contributors" element={<ContributorsPage repoData={repoData} />} />
            <Route path="analytics" element={<AnalyticsPage repoData={repoData} />} />
            <Route path="prs" element={<PullRequestsPage repoData={repoData} />} />
            <Route path="support" element={<SupportPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
