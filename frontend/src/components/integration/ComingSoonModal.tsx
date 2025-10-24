import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Clock } from 'lucide-react';

interface ComingSoonModalProps {
  isOpen: boolean;
  onClose: () => void;
  platform: string;
  icon: React.ReactNode;
}

const ComingSoonModal: React.FC<ComingSoonModalProps> = ({
  isOpen,
  onClose,
  platform,
  icon,
}) => {
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
              <div className="text-yellow-400">{icon}</div>
              <h2 className="text-xl font-bold text-white">{platform} Integration</h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <X size={20} className="text-gray-400" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="inline-flex items-center justify-center w-20 h-20 bg-yellow-500/10 rounded-full mb-4"
            >
              <Clock size={40} className="text-yellow-400" />
            </motion.div>

            <h3 className="text-2xl font-bold text-white mb-2">Coming Soon!</h3>
            <p className="text-gray-400 mb-6">
              We're working hard to bring {platform} integration to Devr.AI. Stay tuned for updates!
            </p>

            <div className="bg-gray-800 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-300">
                Want to be notified when {platform} integration is available?
              </p>
            </div>

            <button
              onClick={onClose}
              className="w-full px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
            >
              Got it!
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default ComingSoonModal;

