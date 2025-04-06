import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface PullRequest {
  id: number;
  title: string;
  author: string;
  status: string;
  comments: number;
  created: string;
}

export default function PullRequestsPage() {
  const [prs] = useState<PullRequest[]>([
    {
      id: 1,
      title: "Add new authentication flow",
      author: "Sarah Chen",
      status: "open",
      comments: 5,
      created: "2 hours ago"
    },
    {
      id: 2,
      title: "Fix responsive layout issues",
      author: "Alex Kumar",
      status: "review",
      comments: 3,
      created: "5 hours ago"
    },
    {
      id: 3,
      title: "Update documentation",
      author: "Maria Garcia",
      status: "merged",
      comments: 2,
      created: "1 day ago"
    }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'text-yellow-500';
      case 'review': return 'text-blue-500';
      case 'merged': return 'text-green-500';
      default: return 'text-gray-500';
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

      <div className="bg-gray-900 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-800">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Author
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Comments
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Created
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {prs.map((pr) => (
              <tr key={pr.id} className="hover:bg-gray-800">
                <td className="px-6 py-4 whitespace-nowrap text-white">{pr.title}</td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-300">{pr.author}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`${getStatusColor(pr.status)} capitalize`}>{pr.status}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-300">{pr.comments}</td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-300">{pr.created}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};
