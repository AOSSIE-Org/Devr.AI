import React from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import ContributorCard from './ContributorCard';
import { RepositoryData } from '../../types';

interface Props {
  repoData: RepositoryData | null;
}

const ContributorsPage: React.FC<Props> = ({ repoData }) => {
  const contributors = repoData?.contributors || [];

  const handleExportReport = () => {
    toast.success('Generating contributor report...');
  };

  const handleInviteContributor = () => {
    toast.success('Opening invitation dialog...');
  };

  if (!repoData) {
    return <div>No data available. Please analyze a repository first.</div>;
  }

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

      {/* Contributors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {contributors.map((contributor) => (
          <ContributorCard
            key={contributor.login}
            name={contributor.login}
            avatar={contributor.avatar_url}
            role="Contributor"
            contributions={contributor.contributions}
            lastActive="N/A"
          />
        ))}
      </div>
    </motion.div>
  );
};

export default ContributorsPage;
