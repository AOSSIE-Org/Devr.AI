import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';

import Sidebar from './components/layout/Sidebar';
import Dashboard from './components/dashboard/Dashboard';
import  BotIntegrationPage from './components/integration/BotIntegrationPage';
import ContributorsPage from './components/contributors/ContributorsPage';
import PullRequestsPage from './components/pages/PullRequestsPage';
import Settings from './components/pages/SettingsPage';


function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activePage, setActivePage] = useState('dashboard');

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard />;
      case 'integration':
        return <BotIntegrationPage />;
      case 'contributors':
        return <ContributorsPage />;
      case 'prs':
        return <PullRequestsPage />;
      case 'settings':
        return <Settings/>;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Sidebar 
        isOpen={isSidebarOpen} 
        setIsOpen={setIsSidebarOpen}
        activePage={activePage}
        setActivePage={setActivePage}
      />
      
      <main className={`transition-all duration-300 ${isSidebarOpen ? 'ml-64' : 'ml-20'}`}>
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