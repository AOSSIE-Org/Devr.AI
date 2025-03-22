import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

export function PlatformDistribution() {
  const platforms = [
    { name: 'GitHub', percentage: 45 },
    { name: 'Discord', percentage: 30 },
    { name: 'Slack', percentage: 15 },
    { name: 'Discourse', percentage: 10 },
  ];

  return (
    <Card className="p-6 bg-[#1A1D24] border-[#2A2F38] text-white">
      <h3 className="text-xl font-semibold mb-6">Platform Distribution</h3>
      <div className="space-y-4">
        {platforms.map((platform) => (
          <div key={platform.name} className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>{platform.name}</span>
              <span>{platform.percentage}%</span>
            </div>
            <Progress value={platform.percentage} className="h-2 bg-[#2A2F38] [&>[role=progressbar]]:bg-cyan-400" />
          </div>
        ))}
      </div>
    </Card>
  );
}