import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Loader2, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface IntegrationModalProps {
  isOpen: boolean;
  onClose: () => void;
  platform: string;
  icon: React.ReactNode;
  onSubmit: (data: IntegrationFormData) => Promise<void>;
  existingData?: {
    organization_name: string;
    config?: any;
  };
}

export interface IntegrationFormData {
  organization_name: string;
  organization_link?: string;  // GitHub org URL or Discord invite link
  config?: any;
}

const IntegrationModal: React.FC<IntegrationModalProps> = ({
  isOpen,
  onClose,
  platform,
  icon,
  onSubmit,
  existingData,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<IntegrationFormData>({
    organization_name: existingData?.organization_name || '',
    organization_link: existingData?.config?.organization_link || '',
    config: existingData?.config || {},
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.organization_name.trim()) {
      newErrors.organization_name = 'Organization name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      await onSubmit(formData);
      toast.success(`${platform} integration ${existingData ? 'updated' : 'created'} successfully!`);
      onClose();
    } catch (error: any) {
      console.error('Error submitting integration:', error);
      toast.error(error.response?.data?.detail || `Failed to ${existingData ? 'update' : 'create'} integration`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof IntegrationFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field when user types
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative w-full max-w-md bg-gray-900 rounded-xl border border-gray-800 shadow-2xl"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-800">
            <div className="flex items-center space-x-3">
              <div className="text-green-400">{icon}</div>
              <h2 className="text-xl font-bold text-white">
                {existingData ? 'Manage' : 'Connect'} {platform}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <X size={20} className="text-gray-400" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Organization Name */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Organization Name
              </label>
              <input
                type="text"
                value={formData.organization_name}
                onChange={(e) => handleChange('organization_name', e.target.value)}
                placeholder={`Enter your ${platform} organization name`}
                className={`w-full px-4 py-2 bg-gray-800 border ${
                  errors.organization_name ? 'border-red-500' : 'border-gray-700'
                } rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-green-500 transition-colors`}
              />
              {errors.organization_name && (
                <p className="mt-1 text-sm text-red-400 flex items-center">
                  <AlertCircle size={14} className="mr-1" />
                  {errors.organization_name}
                </p>
              )}
            </div>

            {/* Organization Link (Optional) */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Organization Link (Optional)
              </label>
              <input
                type={platform.toLowerCase() === 'github' ? 'url' : 'text'}
                value={formData.organization_link || ''}
                onChange={(e) => handleChange('organization_link', e.target.value)}
                placeholder={
                  platform === 'GitHub' 
                    ? 'https://github.com/your-org' 
                    : platform === 'Discord'
                    ? 'Discord Server ID'
                    : 'Organization link'
                }
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-green-500 transition-colors"
              />
              <p className="mt-1 text-xs text-gray-500">
                {platform === 'GitHub' && 'Your GitHub organization URL'}
                {platform === 'Discord' && 'Your Discord server/guild ID (optional)'}
              </p>
            </div>

            {/* Bot Invite Link for Discord */}
            {platform.toLowerCase() === 'discord' && (
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                <p className="text-sm text-blue-400 mb-2">
                  <strong>To add the bot to your Discord server:</strong>
                </p>
                {!import.meta.env.VITE_DISCORD_BOT_INVITE_URL ? (
                <p className="text-sm text-yellow-400">
                  ⚠️ Bot invite URL not configured. Please contact your administrator.
                </p>
              ) : (
                <a
                  href={import.meta.env.VITE_DISCORD_BOT_INVITE_URL || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-sm text-green-400 hover:text-green-300 underline"
                >
                  Click here to invite bot to your server →
                </a>
                )}
                <p className="text-xs text-gray-500 mt-2">
                  After adding the bot, register your server here.
                </p>
              </div>
            )}

            {/* Simple info for GitHub */}
            {platform.toLowerCase() === 'github' && (
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <p className="text-sm text-green-400">
                  ✓ Register your organization here. The bot uses system credentials to access GitHub.
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="mr-2 animate-spin" />
                    {existingData ? 'Updating...' : 'Connecting...'}
                  </>
                ) : (
                  <>{existingData ? 'Update' : 'Connect'}</>
                )}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default IntegrationModal;

