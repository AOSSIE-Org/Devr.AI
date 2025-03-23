import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';

import Sidebar from './components/layout/Sidebar';
import Dashboard from './components/dashboard/Dashboard';
import BotIntegrationPage from './components/integration/BotIntegrationPage';
import ContributorsPage from './components/contributors/ContributorsPage';
import PullRequestsPage from './components/pages/PullRequestsPage';
import SettingsPage from './components/pages/SettingsPage';
import AnalyticsPage from './components/pages/AnalyticsPage';
import SupportPage from './components/pages/SupportPage';
import LandingPage from './components/landing/LandingPage';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activePage, setActivePage] = useState('landing'); // Default to landing page
  const [repoData, setRepoData] = useState<any>(null); // Store fetched repo stats

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
      default:
        return <Dashboard repoData={repoData} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {activePage !== 'landing' && (
        <Sidebar 
          isOpen={isSidebarOpen} 
          setIsOpen={setIsSidebarOpen}
          activePage={activePage}
          setActivePage={setActivePage}
        />
      )}
      
      <main className={`transition-all duration-300 ${isSidebarOpen && activePage !== 'landing' ? 'ml-64' : 'ml-20'}`}>
        <div className="p-8">
          <AnimatePresence mode="wait">
            {renderPage()}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

export default App;
