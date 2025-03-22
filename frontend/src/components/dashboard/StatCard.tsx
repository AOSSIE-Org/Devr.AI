import React from 'react';
import { motion } from 'framer-motion';

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: string;
  trend: number;
}

export default function StatCard({ icon, title, value, trend }: StatCardProps) {
  return (
    <motion.div 
      whileHover={{ scale: 1.02 }}
      className="bg-gray-900 p-6 rounded-xl border border-gray-800 hover:border-green-500 transition-all duration-300"
    >
      <div className="flex items-center justify-between">
        <motion.div 
          initial={{ rotate: 0 }}
          whileHover={{ rotate: 15 }}
          className="text-green-400"
        >
          {icon}
        </motion.div>
        <motion.span 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`text-sm ${trend > 0 ? 'text-green-400' : 'text-yellow-500'}`}
        >
          {trend > 0 ? '+' : ''}{trend}%
        </motion.span>
      </div>
      <h3 className="text-gray-400 mt-4">{title}</h3>
      <motion.p 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-2xl font-bold text-white mt-2"
      >
        {value}
      </motion.p>
    </motion.div>
  );
}
