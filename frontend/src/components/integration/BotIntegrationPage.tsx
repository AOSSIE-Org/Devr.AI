import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { KeyRound, Github, MessageSquare, Slack, MessageCircleQuestion } from 'lucide-react';
import BotIntegration from './BotIntegration';
import { generateApiKey } from '../utils/helpers';
import Modal from '../layout/Modal';
import { Toaster } from 'react-hot-toast';
import { X, Copy } from 'lucide-react';

export default function BotIntegrationPage () {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [activePage, setActivePage] = useState('dashboard');
    const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false);
    const [newApiKey, setNewApiKey] = useState('');

  // const handleManageAPIKeys = () => {
  //   toast.success('Opening API key management...');
  // };
  const handleManageAPIKeys = () => {
    const key = generateApiKey();
    setNewApiKey(key);
    setIsApiKeyModalOpen(true);
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <div className="flex items-center justify-between mb-8">
      <Toaster position="top-right" />
      <Modal 
        isOpen={isApiKeyModalOpen} 
        onClose={() => setIsApiKeyModalOpen(false)}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">New API Key Generated</h2>
          <button 
            onClick={() => setIsApiKeyModalOpen(false)}
            className="p-2 hover:bg-gray-800 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg mb-4">
          <p className="font-mono break-all">{newApiKey}</p>
        </div>
        <div className="flex space-x-4">
          <button
            onClick={() => {
              navigator.clipboard.writeText(newApiKey);
              toast.success('API key copied to clipboard');
            }}
            className="flex-1 bg-green-500 hover:bg-green-600 py-2 rounded-lg transition-colors flex items-center justify-center"
          >
            <Copy size={16} className="mr-2" />
            Copy Key
          </button>
          <button
            onClick={() => setIsApiKeyModalOpen(false)}
            className="flex-1 bg-gray-800 hover:bg-gray-700 py-2 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </Modal>
        <div>
          <h1 className="text-3xl font-bold">Bot Integration</h1>
          <p className="text-gray-400 mt-2">Configure and manage your AI-powered bot integrations</p>
        </div>
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleManageAPIKeys}
          className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors flex items-center"
        >
          <KeyRound size={18} className="mr-2" />
          Manage API Keys
        </motion.button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BotIntegration 
          platform="GitHub"
          icon={<Github size={24} />}
          description="Automate repository management and improve contributor experience"
          features={[
            'Automated issue triage and labeling',
            'Smart PR reviews and suggestions',
            'Welcome messages for first-time contributors',
            'Documentation assistance',
            'Dependency updates'
          ]}
        />
        <BotIntegration 
          platform="Discord"
          icon={<MessageSquare size={24} />}
          description="Build an engaging community space for developers"
          features={[
            'Support channel automation',
            'Role-based access management',
            'Event notifications and reminders',
            'FAQ and documentation search',
            'Community metrics tracking'
          ]}
        />
        <BotIntegration 
          platform="Slack"
          icon={<Slack size={24} />}
          description="Streamline team communication and project updates"
          comingSoon={true}
          features={[
            'Real-time project notifications',
            'Command center for quick actions',
            'Channel monitoring and insights',
            'Integration with CI/CD pipeline',
            'Custom workflow automation'
          ]}
        />
        <BotIntegration 
          platform="Discourse"
          icon={<MessageCircleQuestion size={24} />}
          description="Enhance your community forum experience"
          comingSoon={true}
          features={[
            'Topic categorization',
            'Automated responses',
            'Content moderation',
            'User reputation tracking',
            'Knowledge base management'
          ]}
        />
      </div>
    </motion.div>
  );
};

// export default BotIntegrationPage;