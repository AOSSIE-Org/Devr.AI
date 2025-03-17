import React from 'react';
import {
    BarChart3,
    TrendingUp,
    Users,
    Clock,
    ArrowUpRight,
    ArrowDownRight,
} from 'lucide-react';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '../ui/card';
import {
    Area,
    AreaChart,
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Label,
    Line,
    LineChart,
    Pie,
    PieChart,
    PolarAngleAxis,
    PolarGrid,
    PolarRadiusAxis,
    Radar,
    RadarChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';

const analyticsCards = [
    {
        title: 'Total Users',
        value: '24.8k',
        trend: '+12%',
        isPositive: true,
        description: 'vs last month',
    },
    {
        title: 'Active Sessions',
        value: '1,429',
        trend: '+8%',
        isPositive: true,
        description: 'vs last week',
    },
    {
        title: 'Bounce Rate',
        value: '42%',
        trend: '-3%',
        isPositive: false,
        description: 'vs last week',
    },
    {
        title: 'Avg. Session',
        value: '4m 32s',
        trend: '+12%',
        isPositive: true,
        description: 'vs last month',
    },
];

const timeRanges = [
    'Last 24h',
    'Last Week',
    'Last Month',
    'Last Quarter',
    'Last Year',
];

const areaData = [
    { date: 'Jan', users: 2890, active: 2400 },
    { date: 'Feb', users: 2756, active: 1398 },
    { date: 'Mar', users: 3322, active: 2800 },
    { date: 'Apr', users: 3470, active: 2908 },
    { date: 'May', users: 3475, active: 3000 },
    { date: 'Jun', users: 3129, active: 2800 },
    { date: 'Jul', users: 3490, active: 2978 },
];

const lineData = [
    { name: 'Week 1', value: 150 },
    { name: 'Week 2', value: 230 },
    { name: 'Week 3', value: 224 },
    { name: 'Week 4', value: 218 },
    { name: 'Week 5', value: 335 },
    { name: 'Week 6', value: 247 },
];

const radarData = [
    { subject: 'User 1', A: 120, B: 110, fullMark: 150 },
    { subject: 'User 2', A: 98, B: 130, fullMark: 150 },
    { subject: 'User 3', A: 86, B: 130, fullMark: 150 },
    { subject: 'User 4', A: 99, B: 100, fullMark: 150 },
    { subject: 'User 5', A: 85, B: 90, fullMark: 150 },
    { subject: 'User 6', A: 65, B: 85, fullMark: 150 },
];

const pieData = [
    { name: 'Open', value: 580 },
    { name: 'Closed', value: 484 },
    { name: 'Merged', value: 300 },
    { name: 'Draft', value: 100 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

interface Props {
  repoData: any;
}

const AnalyticsPage: React.FC<Props> = ({ repoData }) => {
  if (!repoData || !repoData.pull_requests) {
    return <div>No data available. Please analyze a repository first.</div>;
  }
    const [selectedRange, setSelectedRange] = React.useState('Last Week');
    const [activeIndex, setActiveIndex] = React.useState(0);

    const onPieEnter = (_: any, index: number) => {
        setActiveIndex(index);
    };

    return (
        <div className="p-8 space-y-8">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-white">
                    Analytics Overview
                </h2>
                <select
                    value={selectedRange}
                    onChange={(e) => setSelectedRange(e.target.value)}
                    className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    {timeRanges.map((range) => (
                        <option key={range} value={range}>
                            {range}
                        </option>
                    ))}
                </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {analyticsCards.map((card) => (
                    <div
                        key={card.title}
                        className="bg-gray-800 rounded-xl p-6 transition-all duration-200 hover:bg-gray-700"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="text-gray-400">{card.title}</h3>
                            {card.isPositive ? (
                                <ArrowUpRight className="text-green-400 w-5 h-5" />
                            ) : (
                                <ArrowDownRight className="text-red-400 w-5 h-5" />
                            )}
                        </div>
                        <div className="flex items-baseline space-x-2">
                            <span className="text-2xl font-bold text-white">
                                {card.value}
                            </span>
                            <span
                                className={`text-sm ${
                                    card.isPositive
                                        ? 'text-green-400'
                                        : 'text-red-400'
                                }`}
                            >
                                {card.trend}
                            </span>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                            {card.description}
                        </p>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>User Growth</CardTitle>
                        <CardDescription>
                            Monthly user acquisition vs active users
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <AreaChart data={areaData}>
                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    stroke="#374151"
                                />
                                <XAxis dataKey="date" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1F2937',
                                        border: '1px solid #374151',
                                        borderRadius: '0.5rem',
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="users"
                                    stroke="#3B82F6"
                                    fill="#3B82F6"
                                    fillOpacity={0.2}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="active"
                                    stroke="#10B981"
                                    fill="#10B981"
                                    fillOpacity={0.2}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Weekly Engagement</CardTitle>
                        <CardDescription>
                            User interaction trends
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={lineData}>
                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    stroke="#374151"
                                />
                                <XAxis dataKey="name" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF">
                                    <Label
                                        value="Interactions"
                                        angle={-90}
                                        position="insideLeft"
                                        style={{ fill: '#9CA3AF' }}
                                    />
                                </YAxis>
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1F2937',
                                        border: '1px solid #374151',
                                        borderRadius: '0.5rem',
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="value"
                                    stroke="#3B82F6"
                                    strokeWidth={2}
                                    dot={{ fill: '#3B82F6' }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Contributor Graph</CardTitle>
                        <CardDescription>
                            contributor activity over time in a repository
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <RadarChart
                                cx="50%"
                                cy="50%"
                                outerRadius="80%"
                                data={radarData}
                            >
                                <PolarGrid stroke="#374151" />
                                <PolarAngleAxis
                                    dataKey="subject"
                                    stroke="#9CA3AF"
                                />
                                <PolarRadiusAxis stroke="#9CA3AF" />
                                <Radar
                                    name="Current"
                                    dataKey="A"
                                    stroke="#3B82F6"
                                    fill="#3B82F6"
                                    fillOpacity={0.2}
                                />
                                <Radar
                                    name="Previous"
                                    dataKey="B"
                                    stroke="#10B981"
                                    fill="#10B981"
                                    fillOpacity={0.2}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1F2937',
                                        border: '1px solid #374151',
                                        borderRadius: '0.5rem',
                                    }}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>PR States</CardTitle>
                        <CardDescription>Pull requests Metrics</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    activeIndex={activeIndex}
                                    activeShape={renderActiveShape}
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                    onMouseEnter={onPieEnter}
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={COLORS[index % COLORS.length]}
                                        />
                                    ))}
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

const renderActiveShape = (props: any) => {
    const {
        cx,
        cy,
        innerRadius,
        outerRadius,
        startAngle,
        endAngle,
        fill,
        payload,
        percent,
        value,
    } = props;

    return (
        <g>
            <text x={cx} y={cy} dy={-4} textAnchor="middle" fill="#9CA3AF">
                {payload.name}
            </text>
            <text x={cx} y={cy} dy={20} textAnchor="middle" fill="#9CA3AF">
                {`${(percent * 100).toFixed(0)}%`}
            </text>
            <text x={cx} y={cy + 35} textAnchor="middle" fill="#9CA3AF">
                {`(${value})`}
            </text>
            <path d={`M${cx},${cy}L${cx},${cy}`} fill="none" stroke={fill} />
        </g>
    );
};

export default AnalyticsPage;