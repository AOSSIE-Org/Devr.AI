import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { Settings, ChevronRight, Shield } from 'lucide-react';
import IntegrationModal, { IntegrationFormData } from './IntegrationModal';
import ComingSoonModal from './ComingSoonModal';
import { apiClient, Platform, Integration } from '../../lib/api';

interface BotIntegrationProps {
  platform: string;
  icon: React.ReactNode;
  description: string;
  features: string[];
  comingSoon?: boolean;
  onIntegrationChange?: () => void;
}

const BotIntegration: React.FC<BotIntegrationProps> = ({ 
  platform, 
  icon, 
  description, 
  features,
  comingSoon = false,
  onIntegrationChange
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [integration, setIntegration] = useState<Integration | null>(null);

  useEffect(() => {
    loadIntegrationStatus();
  }, [platform]);

  const loadIntegrationStatus = async () => {
    try {
      const status = await apiClient.getIntegrationStatus(platform.toLowerCase() as Platform);
      setIsConnected(status.is_connected);
      
      if (status.is_connected) {
        const integrations = await apiClient.getIntegrations();
        const platformIntegration = integrations.find(
          i => i.platform === platform.toLowerCase()
        );
        setIntegration(platformIntegration || null);
      } else {
        setIntegration(null);
      }
    } catch {
      // Silently handle integration status loading errors
      setIsConnected(false);
      setIntegration(null);
    }
  };

  const handleManageClick = () => {
    setIsModalOpen(true);
  };

  const handleSubmitIntegration = async (formData: IntegrationFormData) => {
    try {
      if (integration) {
        await apiClient.updateIntegration(integration.id, {
          organization_name: formData.organization_name,
          organization_link: formData.organization_link,
          config: formData.config,
        });
      } else {
        await apiClient.createIntegration({
          platform: platform.toLowerCase() as Platform,
          organization_name: formData.organization_name,
          organization_link: formData.organization_link,
          config: formData.config,
        });
      }
      
      await loadIntegrationStatus();
      setIsModalOpen(false);
      
      if (onIntegrationChange) {
        onIntegrationChange();
      }
    } catch (error) {
      throw error;
    }
  };

  return (
    <>
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
            {comingSoon ? 'Coming Soon' : isConnected ? 'Connected' : 'Configure'}
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
          onClick={handleManageClick}
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

      {comingSoon ? (
        <ComingSoonModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          platform={platform}
          icon={icon}
        />
      ) : (
        <IntegrationModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          platform={platform}
          icon={icon}
          onSubmit={handleSubmitIntegration}
          existingData={integration ? {
            organization_name: integration.organization_name,
            config: integration.config,
          } : undefined}
        />
      )}
    </>
  );
};

export default BotIntegration;
