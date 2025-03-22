import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { Settings, ChevronRight, Shield } from 'lucide-react';

interface BotIntegrationProps {
  platform: string;
  icon: React.ReactNode;
  connected: boolean;
  description: string;
  features: string[];
}

const BotIntegration: React.FC<BotIntegrationProps> = ({ platform, icon, connected, description, features }) => {
  const [isConnected, setIsConnected] = useState(connected);
  const [isLoading, setIsLoading] = useState(false);

  const handleConnection = async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API call
    setIsConnected(!isConnected);
    setIsLoading(false);
    toast.success(
      isConnected 
        ? `${platform} bot has been disconnected` 
        : `${platform} bot has been connected successfully`
    );
  };

  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="bg-gray-900 p-6 rounded-xl border border-gray-800 hover:border-green-500 transition-all duration-300"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <motion.div 
            whileHover={{ rotate: 20 }}
            className="text-green-400 mr-3"
          >
            {icon}
          </motion.div>
          <div>
            <h3 className="text-white font-semibold">{platform}</h3>
            <p className="text-gray-400 text-sm mt-1">{description}</p>
          </div>
        </div>
        <motion.div 
          animate={{ 
            backgroundColor: isConnected ? 'rgba(34, 197, 94, 0.2)' : 'rgba(234, 179, 8, 0.2)',
            color: isConnected ? 'rgb(34, 197, 94)' : 'rgb(234, 179, 8)'
          }}
          className="px-3 py-1 rounded-full text-sm"
        >
          {isConnected ? 'Connected' : 'Configure'}
        </motion.div>
      </div>
      <div className="space-y-2 mb-4">
        {features.map((feature, index) => (
          <motion.div 
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center text-gray-300 text-sm"
          >
            <Shield size={14} className="mr-2 text-green-400" />
            {feature}
          </motion.div>
        ))}
      </div>
      <motion.button 
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleConnection}
        disabled={isLoading}
        className="w-full mt-4 bg-gray-800 hover:bg-gray-700 text-white py-2 rounded-lg flex items-center justify-center group disabled:opacity-50"
      >
        {isLoading ? (
          <motion.div 
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <Settings size={16} />
          </motion.div>
        ) : (
          <>
            {isConnected ? 'Manage Integration' : 'Connect'} 
            <ChevronRight className="ml-2 group-hover:translate-x-1 transition-transform" size={16} />
          </>
        )}
      </motion.button>
    </motion.div>
  );
};

export default BotIntegration;