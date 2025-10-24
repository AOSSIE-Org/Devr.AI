import React, { useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

interface Props {
  setRepoData: (data: any) => void; // Function to pass data to parent
}

const LandingPage: React.FC<Props> = ({ setRepoData }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const fetchRepoStats = async () => {
    if (!repoUrl) {
      toast.error('Please enter a valid GitHub repository URL.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/repo-stats', { repo_url: repoUrl });
      setRepoData(response.data); // Pass fetched data to parent
      toast.success('Repository stats fetched successfully!');
      navigate('/dashboard'); // Navigate to dashboard
    } catch (error) {
      toast.error('Failed to fetch repository stats. Please check the URL or backend server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="min-h-screen flex items-center justify-center bg-gray-950 text-white"
    >
      <div className="bg-gray-900 p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold mb-4">Welcome to Devr.AI</h1>
        <p className="text-gray-400 mb-6">Enter a GitHub repository URL to analyze its stats.</p>
        <input
          type="text"
          placeholder="https://github.com/owner/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          className="w-full p-3 rounded-lg bg-gray-800 text-white mb-4"
        />
        <button
          onClick={fetchRepoStats}
          disabled={loading}
          className={`w-full py-3 rounded-lg text-white ${loading ? 'bg-gray-700' : 'bg-green-500 hover:bg-green-600'} transition-colors`}
        >
          {loading ? 'Fetching...' : 'Analyze Repository'}
        </button>
      </div>
    </motion.div>
  );
};

export default LandingPage;
