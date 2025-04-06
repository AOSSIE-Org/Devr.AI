import React from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { Users, GitPullRequest, MessageSquare, Activity } from 'lucide-react';
import StatCard from './StatCard';
import BotIntegration from '../integration/BotIntegration';
import { Github, Slack } from 'lucide-react';

export default function Dashboard() {
  const handleNewIntegration = () => {
    toast.success('Creating new integration...');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Dashboard Overview</h1>
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleNewIntegration}
          className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors"
        >
          New Integration
        </motion.button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard 
          icon={<Users size={24} />}
          title="Active Contributors"
          value="1,234"
          trend={12}
        />
        <StatCard 
          icon={<GitPullRequest size={24} />}
          title="Open PRs"
          value="56"
          trend={-3}
        />
        <StatCard 
          icon={<MessageSquare size={24} />}
          title="Community Posts"
          value="892"
          trend={8}
        />
        <StatCard 
          icon={<Activity size={24} />}
          title="Response Rate"
          value="94%"
          trend={5}
        />
      </div>

      <h2 className="text-2xl font-bold mb-6">Quick Actions</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <BotIntegration 
          platform="GitHub"
          icon={<Github size={24} />}
          connected={true}
          description="Automate your GitHub workflow"
          features={['Issue triage', 'PR reviews', 'Welcome messages']}
        />
        <BotIntegration 
          platform="Discord"
          icon={<MessageSquare size={24} />}
          connected={false}
          description="Engage with your community"
          features={['Support channels', 'Role management', 'Event notifications']}
        />
        <BotIntegration 
          platform="Slack"
          icon={<Slack size={24} />}
          connected={true}
          description="Team collaboration hub"
          features={['Channel monitoring', 'Instant notifications', 'Command center']}
        />
      </div>
    </motion.div>
  );
};

// export default Dashboard;