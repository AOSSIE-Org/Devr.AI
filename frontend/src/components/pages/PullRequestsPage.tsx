import React from 'react';
import { motion } from 'framer-motion';
import { RepositoryData } from '../../types';

interface Props {
  repoData: RepositoryData | null;
}

const PullRequestsPage: React.FC<Props> = ({ repoData }) => {
  if (!repoData || !repoData.pull_requests) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-gray-400 font-medium">
        <p className="text-xl">No data available. Please analyze a repository first.</p>
      </div>
    );
  }

  const prs = repoData.pull_requests.details || [];

  const getStatusColor = (state: string) => {
    switch (state.toLowerCase()) {
      case 'open':
        return 'text-yellow-500';
      case 'closed':
        return 'text-red-500';
      case 'merged':
        return 'text-green-500';
      case 'review':
        return 'text-blue-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Pull Requests</h1>
      </div>

      {prs.length === 0 ? (
        <div className="bg-gray-900 p-12 rounded-xl text-center text-gray-400">
          No pull requests found for this repository.
        </div>
      ) : (
        <div className="bg-gray-900 rounded-xl overflow-hidden border border-gray-800">
          <table className="w-full">
            <thead className="bg-gray-800/50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Title</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Author</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">PR Number</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Link</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {prs.map((pr) => (
                <tr key={pr.number} className="hover:bg-gray-800/30 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-white font-medium">{pr.title}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <img src={pr.author.avatar_url} alt={pr.author.login} className="w-8 h-8 rounded-full border border-gray-700" />
                      <a href={pr.author.profile_url} target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300 transition-colors text-sm">
                        {pr.author.login}
                      </a>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`${getStatusColor(pr.state)} capitalize px-2 py-1 bg-gray-800 rounded text-xs font-semibold`}>
                      {pr.state}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-400 text-sm font-mono">#{pr.number}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <a href={pr.url} target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300 underline text-sm">
                      View PR
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
};

export default PullRequestsPage;
