import React from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import ContributorCard from './ContributorCard';

export default function ContributorsPage() {
  const handleExportReport = () => {
    toast.success('Generating contributor report...');
  };

  const handleInviteContributor = () => {
    toast.success('Opening invitation dialog...');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Contributors</h1>
          <p className="text-gray-400 mt-2">Manage and track contributor activity</p>
        </div>
        <div className="flex space-x-4">
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleExportReport}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            Export Report
          </motion.button>
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleInviteContributor}
            className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors"
          >
            Invite Contributor
          </motion.button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ContributorCard 
          name="Sarah Chen"
          avatar="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100"
          role="Core Maintainer"
          contributions="234"
          lastActive="2 hours ago"
        />
        <ContributorCard 
          name="Alex Kumar"
          avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100"
          role="Documentation Lead"
          contributions="156"
          lastActive="1 day ago"
        />
        <ContributorCard 
          name="Maria Garcia"
          avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100"
          role="Security Team"
          contributions="198"
          lastActive="3 hours ago"
        />
        <ContributorCard 
          name="James Wilson"
          avatar="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100"
          role="Feature Developer"
          contributions="145"
          lastActive="5 hours ago"
        />
        <ContributorCard 
          name="Emily Zhang"
          avatar="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100"
          role="UI/UX Designer"
          contributions="167"
          lastActive="Just now"
        />
        <ContributorCard 
          name="David Park"
          avatar="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100"
          role="Testing Lead"
          contributions="123"
          lastActive="2 days ago"
        />
      </div>
    </motion.div>
  );
};
