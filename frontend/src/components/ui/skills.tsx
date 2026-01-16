import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X } from 'lucide-react';

interface SkillSectionProps {
  title: string;
  icon: React.ReactNode;
  items: string[];
  type: 'languages' | 'frameworks';
  inputValue: string;
  setInputValue: (val: string) => void;
  isEditing: boolean;
  onAdd: (type: 'languages' | 'frameworks', val: string) => void;
  onRemove: (type: 'languages' | 'frameworks', val: string) => void;
}

const SkillSection: React.FC<SkillSectionProps> = ({ 
  title, 
  icon, 
  items, 
  type, 
  inputValue, 
  setInputValue,
  isEditing,
  onAdd,
  onRemove
}) => {
  return (
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-400 mb-2">{title}</label>
      <div className="flex items-start space-x-3">
        <div className="mt-1 text-gray-400">{icon}</div>
        <div className="w-full">
          <div className="flex flex-wrap gap-2 mb-2">
            <AnimatePresence>
              {items.map((item, index) => (
                <motion.span 
                  key={`${type}-${index}`}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className={`px-2 py-1 rounded text-sm border flex items-center group ${
                    type === 'languages' 
                      ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' 
                      : 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                  }`}
                >
                  {item}
                  {isEditing && (
                    <button 
                      onClick={() => onRemove(type, item)}
                      className="ml-1.5 hover:text-red-400 transition-colors"
                    >
                      <X size={12} />
                    </button>
                  )}
                </motion.span>
              ))}
            </AnimatePresence>
          </div>
          
          {isEditing && (
            <div className="relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    onAdd(type, inputValue);
                  }
                }}
                placeholder={`Add ${title.toLowerCase()}...`}
                className="bg-transparent text-white text-sm focus:outline-none border-b border-gray-700 focus:border-green-500 w-full pb-1 transition-colors"
              />
              <Plus size={14} className="absolute right-0 top-1 text-gray-500" />
            </div>
          )}
          
          {!isEditing && items.length === 0 && (
            <span className="text-gray-600 italic text-sm">None listed</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default SkillSection;