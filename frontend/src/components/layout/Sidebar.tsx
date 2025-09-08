import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Bot, 
  Users,
  Activity,
  GitPullRequest,
  MessageCircleQuestion,
  Menu,
  Settings,
  User,
  LogOut
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  onLogout: () => void;
}

const navItems = [
  { icon: <LayoutDashboard size={20} />, label: 'Dashboard', path: '/dashboard' },
  { icon: <Bot size={20} />, label: 'Bot Integration', path: '/integration' },
  { icon: <Users size={20} />, label: 'Contributors', path: '/contributors' },
  { icon: <Activity size={20} />, label: 'Analytics', path: '/analytics' },
  { icon: <GitPullRequest size={20} />, label: 'Pull Requests', path: '/prs' },
  { icon: <MessageCircleQuestion size={20} />, label: 'Support', path: '/support' },
  { icon: <Settings size={20} />, label: 'Settings', path: '/settings' },
  { icon: <User size={20} />, label: 'Profile', path: '/profile' },
];

const Sidebar: React.FC<SidebarProps> = ({ isOpen, setIsOpen, onLogout }) => (
  <div className={`fixed top-0 left-0 h-full bg-gray-900 text-white transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-20'} flex flex-col`}>
    <div>
      <div className="p-4 flex items-center justify-between">
        <h2 className={`font-bold text-xl ${!isOpen && 'hidden'}`}>Devr.AI</h2>
        <button onClick={() => setIsOpen(!isOpen)} className="p-2 hover:bg-gray-800 rounded-lg">
          <Menu size={20} />
        </button>
      </div>
      
      <nav className="mt-8">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `w-full flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-green-400 transition-colors ${
                isActive ? 'bg-gray-800 text-green-400' : ''
              }`
            }
          >
            {item.icon}
            <span className={`ml-4 ${!isOpen && 'hidden'}`}>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
    <div className="mt-auto p-4">
        <button
          onClick={onLogout}
          className={`w-full flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-red-500 transition-colors`}
        >
          <LogOut size={20} />
          <span className={`ml-4 ${!isOpen && 'hidden'}`}>Logout</span>
        </button>
      </div>
  </div>
);

export default Sidebar;
