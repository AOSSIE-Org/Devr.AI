import React from 'react';
import { 
  LayoutDashboard, 
  Bot, 
  Github, 
  MessageSquare, 
  Users,
  Activity,
  GitPullRequest,
  MessageCircleQuestion,
  Menu,
  Settings,
  User
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  activePage: string;
  setActivePage: (page: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, setIsOpen, activePage, setActivePage }) => (
  <div className={`fixed top-0 left-0 h-full bg-gray-900 text-white transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-20'}`}>
    <div className="p-4 flex items-center justify-between">
      <h2 className={`font-bold text-xl ${!isOpen && 'hidden'}`}>Devr.AI</h2>
      <button onClick={() => setIsOpen(!isOpen)} className="p-2 hover:bg-gray-800 rounded-lg">
        <Menu size={20} />
      </button>
    </div>
    
    <nav className="mt-8">
      {[
        { icon: <LayoutDashboard size={20} />, label: 'Dashboard', id: 'dashboard' },
        { icon: <Bot size={20} />, label: 'Bot Integration', id: 'integration' },
        { icon: <Users size={20} />, label: 'Contributors', id: 'contributors' },
        { icon: <Activity size={20} />, label: 'Analytics', id: 'analytics' },
        { icon: <GitPullRequest size={20} />, label: 'Pull Requests', id: 'prs' },
        { icon: <MessageCircleQuestion size={20} />, label: 'Support', id: 'support' },
        { icon: <Settings size={20} />, label: 'Settings', id: 'settings' },
        { icon: <User size={20} />, label: 'Profile', id: 'profile' },
      ].map((item) => (
        <button
          key={item.id}
          onClick={() => setActivePage(item.id)}
          className={`w-full flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-green-400 transition-colors ${
            activePage === item.id ? 'bg-gray-800 text-green-400' : ''
          }`}
        >
          {item.icon}
          <span className={`ml-4 ${!isOpen && 'hidden'}`}>{item.label}</span>
        </button>
      ))}
    </nav>
  </div>
);

export default Sidebar;