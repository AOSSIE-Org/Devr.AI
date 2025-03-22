import { Activity, GitBranch, MessageSquare, Users2, HelpCircle, Settings, BarChart2, Clock, GitPullRequest } from 'lucide-react';

export function Sidebar() {
  const menuItems = [
    { icon: Activity, label: 'Dashboard', active: true },
    { icon: GitBranch, label: 'GitHub Integration' },
    { icon: MessageSquare, label: 'Community Chat' },
    { icon: Users2, label: 'Contributors' },
    { icon: GitPullRequest, label: 'PR Assistance' },
    { icon: Clock, label: 'Issue Triage' },
    { icon: BarChart2, label: 'Analytics' },
    { icon: Settings, label: 'Settings' },
    { icon: HelpCircle, label: 'Help & Support' },
  ];

  return (
    <div className="w-64 bg-[#0F1116] h-screen p-4 flex flex-col">
      <div className="flex items-center gap-2 px-2 py-4">
        <div className="w-12 h-12 bg-cyan-400 rounded-full flex items-center justify-center text-black font-bold">
          DEVR
        </div>
        <span className="text-white font-semibold">Devr.AI</span>
      </div>
      <nav className="mt-6">
        {menuItems.map((item) => (
          <div
            key={item.label}
            className={`flex items-center gap-3 px-3 py-2 rounded-lg mb-1 cursor-pointer ${
              item.active ? 'bg-[#1A1D24] text-cyan-400' : 'text-gray-400 hover:bg-[#1A1D24] hover:text-gray-200'
            }`}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </div>
        ))}
      </nav>
    </div>
  );
}