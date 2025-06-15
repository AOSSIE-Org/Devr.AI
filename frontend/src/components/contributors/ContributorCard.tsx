import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';

interface ContributorCardProps {
  name: string;
  avatar: string;
  role: string;
  contributions: number; // Changed to number for consistency
  lastActive?: string; // Made optional for flexibility
}

const ContributorCard: React.FC<ContributorCardProps> = ({ name, avatar, role, contributions, lastActive }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-gray-900 p-6 rounded-xl border border-gray-800 hover:border-green-500 transition-all duration-300 cursor-pointer"
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="flex items-center space-x-4">
        <motion.img
          whileHover={{ scale: 1.1 }}
          src={avatar}
          alt={name}
          className="w-12 h-12 rounded-full"
        />
        <div>
          <h3 className="text-white font-semibold">{name}</h3>
          <p className="text-gray-400 text-sm">{role}</p>
        </div>
      </div>

      <motion.div
        initial={false}
        animate={{ height: isExpanded ? 'auto' : 0}}
        className="mt-4 space-y-2"
      >
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Contributions</span>
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-green-400"
          >
            {contributions}
          </motion.span>
        </div>
        
        {lastActive && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Last Active</span>
            <span className="text-gray-300">{lastActive}</span>
          </div>
        )}
        
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="pt-4 border-t border-gray-800 mt-4"
          >
            <button
              onClick={(e) => {
                e.stopPropagation();
                toast.success(`Message sent to ${name}`);
              }}
              className="w-full bg-green-500 hover:bg-green-600 text-white py-2 rounded-lg transition-colors"
            >
              Send Message
            </button>
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  );
};

export default ContributorCard;
