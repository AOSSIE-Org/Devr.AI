import { Users2, Clock, GitPullRequest, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { StatCard } from '@/components/dashboard/StatCard';
import { ContributorActivity } from '@/components/dashboard/ContributorActivity';
import { PlatformDistribution } from '@/components/dashboard/PlatformDistribution';
import { RecentContributors } from '@/components/dashboard/RecentContributors';
import { RecentIssues } from '@/components/dashboard/RecentIssues';
import { AIAssistantActivity } from '@/components/dashboard/AIAssistantActivity';

function App() {
  return (
    <div className="flex bg-[#0F1116] min-h-screen text-white">
      <Sidebar />
      <main className="flex-1 p-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">WELCOME TO DEVR</h1>
            <p className="text-gray-400 max-w-2xl mt-4">
              Devr.AI is your AI-powered Developer Relations assistant, helping you engage with contributors, 
              onboard new developers, and provide real-time project updates across platforms.
            </p>
            <Button className="mt-6 bg-cyan-400 text-black hover:bg-cyan-500">Get Started</Button>
          </div>
          <div className="w-32 h-32 relative">
            <div className="w-full h-full rounded-full border-4 border-cyan-400 animate-spin-slow"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold">DEVR</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-6 mb-6">
          <StatCard title="Active Contributors" value="128" icon={Users2} change="12%" />
          <StatCard title="Open Issues" value="45" icon={Clock} change="5%" changeType="negative" />
          <StatCard title="Pull Requests" value="81" icon={GitPullRequest} change="23%" />
          <StatCard title="Community Messages" value="539" icon={MessageSquare} change="8%" />
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <ContributorActivity />
          <PlatformDistribution />
        </div>

        <div className="grid grid-cols-3 gap-6">
          <RecentContributors />
          <RecentIssues />
          <AIAssistantActivity />
        </div>
      </main>
    </div>
  );
}

export default App;