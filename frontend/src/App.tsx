import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
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
import ForgotPasswrdPage from './components/pages/ForgotPasswrdPage';
import ResetPasswordPage from './components/pages/ResetPasswordPage';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activePage, setActivePage] = useState('landing'); // Default to landing page
  const [repoData, setRepoData] = useState<any>(null); // Store fetched repo stats
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  //Auto login if user has already logged in
  useEffect(() => {
    supabase.auth.getSession().then(({ data, error }) => {
      if (error) {
        toast.error('User Login Failed');
        console.error('Error checking session:', error);
        return;
      }
      setIsAuthenticated(!!data.session);
    });

    const { data: subscription } = supabase.auth.onAuthStateChange(
      (event, session) => {
        console.log("Auth event:", event, session);
        switch(event){
        case "SIGNED_IN":
          setIsAuthenticated(true);
          toast.success("Signed in!");
          break;

        case "SIGNED_OUT":
          setIsAuthenticated(false);
          setActivePage("landing");
          setRepoData(null);
          toast.success("Signed out!");
          break;

        case "PASSWORD_RECOVERY":
          toast("Check your email to reset your password.");
          break;
        case "TOKEN_REFRESHED":
          console.log("Session refreshed");
          break;
        case "USER_UPDATED":
          console.log("User updated", session?.user);
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
      console.error('Error during logout:', error);
      return;
    }
    toast.success('Signed out!');
    setIsAuthenticated(false);
    setActivePage('landing');
    setRepoData(null);
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
        return <ProfilePage onSignOut={handleLogout} />;
      default:
        return <Dashboard repoData={repoData} />;
    }
  };

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
                <ForgotPasswrdPage />
              )
            }
          />
          <Route
            path="/reset-password"
            element={
              <ResetPasswordPage/>
            }
          />
          <Route
            path="/signup"
            element= {isAuthenticated ? (
                <Navigate to="/" replace />
              ) : (
                <SignUpPage/>
              )}
          />
          <Route
            path="/*"
            element={
              isAuthenticated ? (
                <div className="flex">
                  <Sidebar
                    isOpen={isSidebarOpen}
                    setIsOpen={setIsSidebarOpen}
                    activePage={activePage}
                    setActivePage={setActivePage}
                  />
                  <main
                    className={`transition-all duration-300 flex-1 ${
                      isSidebarOpen ? 'ml-64' : 'ml-20'
                    }`}
                  >
                    <div className="p-8">
                      <AnimatePresence mode="wait">{renderPage()}</AnimatePresence>
                    </div>
                  </main>
                </div>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
