import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar } from '@/components/ui/avatar';

export function RecentContributors() {
  const contributors = [
    { initials: 'AJ', name: 'Alex Johnson', role: 'Frontend Developer', timeAgo: '2 hours ago' },
    { initials: 'SC', name: 'Sarah Chen', role: 'Backend Engineer', timeAgo: '5 hours ago' },
    { initials: 'MR', name: 'Miguel Rodriguez', role: 'DevOps', timeAgo: '1 day ago' },
    { initials: 'PS', name: 'Priya Sharma', role: 'UI/UX Designer', timeAgo: '2 days ago' },
  ];

  return (
    <Card className="p-6 bg-[#1A1D24] border-[#2A2F38] text-white">
      <h3 className="text-xl font-semibold mb-6">Recent Contributors</h3>
      <div className="space-y-4">
        {contributors.map((contributor) => (
          <div key={contributor.name} className="flex items-center gap-4">
            <Avatar className="bg-cyan-400 text-black">
              <span className="font-semibold">{contributor.initials}</span>
            </Avatar>
            <div className="flex-1">
              <p className="font-medium">{contributor.name}</p>
              <p className="text-sm text-gray-400">{contributor.role}</p>
            </div>
            <span className="text-sm text-gray-400">{contributor.timeAgo}</span>
          </div>
        ))}
      </div>
      <Button variant="link" className="text-cyan-400 p-0 mt-4">
        View all contributors
      </Button>
    </Card>
  );
}