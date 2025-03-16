import { DivideIcon as LucideIcon } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface StatCardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  change?: string;
  changeType?: 'positive' | 'negative';
}

export function StatCard({ title, value, icon: Icon, change, changeType = 'positive' }: StatCardProps) {
  return (
    <Card className="p-6 bg-[#1A1D24] border-[#2A2F38] text-white">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-400 mb-2">{title}</p>
          <h3 className="text-3xl font-bold">{value}</h3>
          {change && (
            <p className={`text-sm mt-2 ${changeType === 'positive' ? 'text-green-500' : 'text-red-500'}`}>
              {changeType === 'positive' ? '+' : '-'}{change} from last month
            </p>
          )}
        </div>
        <Icon className="text-cyan-400" size={24} />
      </div>
    </Card>
  );
}