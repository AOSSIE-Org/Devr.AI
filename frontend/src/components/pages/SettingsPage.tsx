import React, { useState, useEffect } from 'react';
import { Copy, Eye, EyeOff, Trash } from 'lucide-react';

interface ApiKey {
  id: string;
  name: string;
  value: string;
  createdAt: string;
  lastUsed?: string;
}

export default function SettingsPage () {
  // State declarations
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [newKeyName, setNewKeyName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [newlyGeneratedKey, setNewlyGeneratedKey] = useState('');
  const [showKeyValues, setShowKeyValues] = useState<Record<string, boolean>>({});
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Effect for initial data load
  useEffect(() => {
    // Mock data - in a real app, you would fetch this from your backend
    const mockApiKeys: ApiKey[] = [
      { id: '1', name: 'Production Key', value: 'sk_prod_1234567890abcdef', createdAt: '2025-02-01T10:30:00Z', lastUsed: '2025-03-15T08:45:12Z' },
      { id: '2', name: 'Development Key', value: 'sk_dev_0987654321fedcba', createdAt: '2025-02-15T14:20:00Z', lastUsed: '2025-03-14T16:22:45Z' },
      { id: '3', name: 'Test Environment', value: 'sk_test_abcdef1234567890', createdAt: '2025-02-28T09:15:00Z', lastUsed: '2025-03-10T11:05:30Z' },
    ];
    
    setApiKeys(mockApiKeys);
    
    // Initialize visibility state for each key
    const initialVisibility: Record<string, boolean> = {};
    mockApiKeys.forEach(key => {
      initialVisibility[key.id] = false;
    });
    setShowKeyValues(initialVisibility);
  }, []);

  // Function to generate a new API key
  const generateNewApiKey = () => {
    if (!newKeyName.trim()) return;
    
    setIsGenerating(true);
    
    // Simulate API call to generate a new key
    setTimeout(() => {
      const random1 = Math.random().toString(36).substring(2, 15);
      const random2 = Math.random().toString(36).substring(2, 15);
      
      const newKey: ApiKey = {
        id: Date.now().toString(),
        name: newKeyName,
        value: `sk_${random1}${random2}`,
        createdAt: new Date().toISOString(),
      };
      
      setApiKeys([newKey, ...apiKeys]);
      setNewlyGeneratedKey(newKey.value);
      setNewKeyName('');
      setIsGenerating(false);
      setIsDialogOpen(true);
    }, 500);
  };

  // Function to delete an API key
  const deleteApiKey = (id: string) => {
    if (window.confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      setApiKeys(apiKeys.filter(key => key.id !== id));
    }
  };

  // Function to toggle API key visibility
  const toggleKeyVisibility = (id: string) => {
    setShowKeyValues({
      ...showKeyValues,
      [id]: !showKeyValues[id]
    });
  };

  // Function to copy text to clipboard
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Simple alert instead of toast notification
    alert('Copied to clipboard!');
  };

  // Function to format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Component rendering
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">API Settings</h1>
      
      {/* Create API Key Card */}
      <div className="bg-white rounded-lg shadow-md mb-8 overflow-hidden">
        <div className="p-6">
          <h2 className="text-xl font-semibold mb-1">Create API Key</h2>
          <p className="text-gray-500 mb-4">
            Generate a new API key for authentication with our services.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="w-full sm:max-w-sm">
              <label htmlFor="apiKeyName" className="block text-sm font-medium text-gray-700 mb-1">
                API Key Name
              </label>
              <input
                id="apiKeyName"
                type="text"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                placeholder="e.g., Production Server"
                className="block text-black w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button 
              onClick={generateNewApiKey}
              disabled={isGenerating || !newKeyName.trim()}
              className={`mt-4 sm:mt-auto inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-sm py-2 px-4 bg-green-600 text-white hover:bg-green-700 ${isGenerating || !newKeyName.trim() ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              {isGenerating ? 'Generating...' : 'Generate New API Key'}
            </button>
          </div>
        </div>
      </div>
      
      {/* API Keys List Card */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6">
          <h2 className="text-xl font-semibold mb-1">Your API Keys</h2>
          <p className="text-gray-500 mb-4">
            Manage your existing API keys. Keep these secure and never share them publicly.
          </p>
          
          {apiKeys.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      API Key
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Used
                    </th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {apiKeys.map((key) => (
                    <tr key={key.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {key.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex items-center gap-2">
                          <span className="font-mono">
                            {showKeyValues[key.id] ? key.value : `${key.value.substring(0, 10)}...`}
                          </span>
                          <button 
                            className="p-1 bg-transparent hover:bg-gray-100 rounded-md focus:outline-none"
                            onClick={() => toggleKeyVisibility(key.id)}
                          >
                            {showKeyValues[key.id] ? (
                              <EyeOff size={16} />
                            ) : (
                              <Eye size={16} />
                            )}
                          </button>
                          <button 
                            className="p-1 bg-transparent hover:bg-gray-100 rounded-md focus:outline-none"
                            onClick={() => copyToClipboard(key.value)}
                          >
                            <Copy size={16} />
                          </button>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(key.createdAt)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {key.lastUsed ? formatDate(key.lastUsed) : "Never used"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button 
                          className="inline-flex items-center justify-center rounded-md text-sm py-1 px-3 bg-red-600 text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                          onClick={() => deleteApiKey(key.id)}
                        >
                          <Trash size={16} className="mr-1" /> Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No API keys found. Generate your first key above.
            </div>
          )}
        </div>
      </div>

      {/* New API Key Dialog */}
      {isDialogOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="fixed inset-0 bg-black opacity-30" onClick={() => setIsDialogOpen(false)}></div>
          <div className="bg-white rounded-lg shadow-lg z-10 w-full max-w-md mx-4 p-6">
            <div className="mb-4">
              <h3 className="text-lg font-medium mb-1">API Key Generated</h3>
              <p className="text-gray-500 text-sm">
                Please copy your new API key now. For security reasons, you won't be able to see the full key again.
              </p>
            </div>
            <div className="bg-gray-100 p-4 rounded-md mb-4">
              <code className="text-sm font-mono break-all text-black">{newlyGeneratedKey}</code>
            </div>
            <div className="flex justify-end gap-3">
              <button 
                className="inline-flex items-center justify-center rounded-md text-sm py-2 px-4 bg-green-600 text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                onClick={() => copyToClipboard(newlyGeneratedKey)}
              >
                <Copy size={16} className="mr-2" /> Copy to clipboard
              </button>
              <button 
                className="inline-flex items-center justify-center rounded-md text-sm py-2 px-4 bg-gray-200 text-gray-800 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                onClick={() => setIsDialogOpen(false)}
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
