import { Card } from '@/components/ui/card';

export function AIAssistantActivity() {
  const activities = [
    { action: 'Answered question about API usage', platform: 'Discord', timeAgo: '10 minutes ago' },
    { action: 'Triaged new issue #1234', platform: 'GitHub', timeAgo: '45 minutes ago' },
    { action: 'Welcomed new contributor', platform: 'Slack', timeAgo: '2 hours ago' },
    { action: 'Provided PR feedback', platform: 'GitHub', timeAgo: '3 hours ago' },
  ];

  const stats = [
    { label: 'Questions Answered', value: '1,245' },
    { label: 'Issues Triaged', value: '328' },
    { label: 'PRs Reviewed', value: '156' },
    { label: 'Response Time', value: '2.4m' },
  ];

  return (
    <Card className="p-6 bg-[#1A1D24] border-[#2A2F38] text-white">
      <h3 className="text-xl font-semibold mb-6">AI Assistant Activity</h3>
      <div className="space-y-4 mb-6">
        {activities.map((activity) => (
          <div key={activity.action} className="p-4 bg-[#2A2F38] rounded-lg">
            <p className="font-medium mb-1">{activity.action}</p>
            <div className="flex justify-between text-sm text-gray-400">
              <span>{activity.platform}</span>
              <span>{activity.timeAgo}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="border border-cyan-400/20 rounded-lg p-4">
        <h4 className="text-cyan-400 mb-4">AI Assistant Stats</h4>
        <div className="grid grid-cols-2 gap-4">
          {stats.map((stat) => (
            <div key={stat.label}>
              <p className="text-gray-400 text-sm">{stat.label}</p>
              <p className="text-xl font-bold">{stat.value}</p>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}