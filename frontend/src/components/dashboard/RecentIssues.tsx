import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export function RecentIssues() {
  const issues = [
    { title: 'Fix authentication bug in login flow', priority: 'High', status: 'Open' },
    { title: 'Update documentation for API v2', priority: 'Medium', status: 'In Progress' },
    { title: 'Improve mobile responsiveness', priority: 'Medium', status: 'Open' },
    { title: 'Add dark mode support', priority: 'Low', status: 'Open' },
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-500/20 text-red-500';
      case 'medium': return 'bg-yellow-500/20 text-yellow-500';
      case 'low': return 'bg-blue-500/20 text-blue-500';
      default: return 'bg-gray-500/20 text-gray-500';
    }
  };

  return (
    <Card className="p-6 bg-[#1A1D24] border-[#2A2F38] text-white">
      <h3 className="text-xl font-semibold mb-6">Recent Issues</h3>
      <div className="space-y-4">
        {issues.map((issue) => (
          <div key={issue.title} className="p-4 bg-[#2A2F38] rounded-lg">
            <h4 className="font-medium mb-2">{issue.title}</h4>
            <div className="flex gap-2">
              <Badge variant="secondary" className={getPriorityColor(issue.priority)}>
                {issue.priority}
              </Badge>
              <Badge variant="secondary" className={issue.status === 'Open' ? 'bg-green-500/20 text-green-500' : 'bg-purple-500/20 text-purple-500'}>
                {issue.status}
              </Badge>
            </div>
          </div>
        ))}
      </div>
      <Button variant="link" className="text-cyan-400 p-0 mt-4">
        View all issues
      </Button>
    </Card>
  );
}