import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export function ContributorActivity() {
  return (
    <Card className="p-6 bg-[#1A1D24] border-[#2A2F38] text-white">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-semibold">Contributor Activity</h3>
        <Select defaultValue="7days">
          <SelectTrigger className="w-[140px] bg-[#2A2F38] border-0">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7days">Last 7 days</SelectItem>
            <SelectItem value="30days">Last 30 days</SelectItem>
            <SelectItem value="3months">Last 3 months</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="h-[200px] flex items-end justify-between gap-2">
        {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
          <div key={day} className="flex flex-col items-center gap-2 flex-1">
            <div className="w-full bg-cyan-400/20 rounded-sm" style={{ height: `${Math.random() * 150 + 20}px` }}></div>
            <span className="text-sm text-gray-400">{day}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}