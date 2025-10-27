import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import toast, { Toaster } from 'react-hot-toast';

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
import { supabase } from './lib/supabaseClient';
import ForgotPasswordPage from './components/pages/ForgotPasswordPage';
import ResetPasswordPage from './components/pages/ResetPasswordPage';

// Define proper TypeScript interfaces
interface RepositoryData {
  id: string;
  name: string;
  full_name: string;
  description?: string;
  html_url: string;
  stargazers_count: number;
  forks_count: number;
  language?: string;
  created_at: string;
  updated_at: string;
  owner: {
    login: string;
    avatar_url: string;
  };
}

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [repoData, setRepoData] = useState<RepositoryData | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Auto login if user has already logged in
  useEffect(() => {
    supabase.auth.getSession().then(({ data, error }) => {
      if (error) {
        toast.error('User Login Failed');
        // Log error internally without exposing in production console
        return;
      }
      setIsAuthenticated(!!data.session);
    });

    const { data: subscription } = supabase.auth.onAuthStateChange(
      (event, session) => {
        switch (event) {
          case "SIGNED_IN":
            setIsAuthenticated(true);
            toast.success("Signed in!");
            break;

          case "SIGNED_OUT":
            setIsAuthenticated(false);
            setRepoData(null);
            toast.success("Signed out!");
            break;

          case "PASSWORD_RECOVERY":
            toast("Check your email to reset your password.");
            break;
          case "TOKEN_REFRESHED":
            // Session refreshed silently
            break;
          case "USER_UPDATED":
            // User profile updated
            break;
        }
      }
    );

    return () => {
      subscription.subscription.unsubscribe();
    };
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      toast.error('Logout failed');
      // Log error internally without exposing in production console
      return;
    }
    toast.success('Signed out!');
    setIsAuthenticated(false);
    setRepoData(null);
  };

  const ProtectedLayout = () => (
    <div className="flex">
      <Sidebar
        isOpen={isSidebarOpen}
        setIsOpen={setIsSidebarOpen}
        onLogout={handleLogout}
      />
      <main
        className={`transition-all duration-300 flex-1 ${
          isSidebarOpen ? 'ml-64' : 'ml-20'
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
