"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

interface ContributorDistributionProps {
  timeFilter: "day" | "week" | "month"
}

export default function ContributorDistribution({ timeFilter }: ContributorDistributionProps) {
  const [activeTab, setActiveTab] = useState("platform")

  // Dynamic data based on time filter and active tab
  const getData = () => {
    if (activeTab === "platform") {
      if (timeFilter === "day") {
        return [
          { name: "GitHub", value: 120, color: "#06B6D4" },
          { name: "Discord", value: 85, color: "#8B5CF6" },
          { name: "Slack", value: 65, color: "#F59E0B" },
          { name: "Discourse", value: 45, color: "#EC4899" },
        ]
      } else if (timeFilter === "week") {
        return [
          { name: "GitHub", value: 145, color: "#06B6D4" },
          { name: "Discord", value: 95, color: "#8B5CF6" },
          { name: "Slack", value: 75, color: "#F59E0B" },
          { name: "Discourse", value: 55, color: "#EC4899" },
        ]
      } else {
        return [
          { name: "GitHub", value: 180, color: "#06B6D4" },
          { name: "Discord", value: 120, color: "#8B5CF6" },
          { name: "Slack", value: 90, color: "#F59E0B" },
          { name: "Discourse", value: 70, color: "#EC4899" },
        ]
      }
    } else if (activeTab === "region") {
      return [
        { name: "North America", value: 35, color: "#06B6D4" },
        { name: "Europe", value: 30, color: "#8B5CF6" },
        { name: "Asia", value: 25, color: "#F59E0B" },
        { name: "Other", value: 10, color: "#EC4899" },
      ]
    } else {
      return [
        { name: "Core", value: 15, color: "#06B6D4" },
        { name: "Regular", value: 25, color: "#8B5CF6" },
        { name: "Occasional", value: 35, color: "#F59E0B" },
        { name: "First-time", value: 25, color: "#EC4899" },
      ]
    }
  }

  const data = getData()

  const RADIAN = Math.PI / 180
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }: any) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? "start" : "end"}
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  return (
    <motion.div
      className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 shadow-lg shadow-black/20 overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-1">Contributor Distribution</h2>
        <p className="text-gray-400 text-sm">Active contributors by {activeTab}</p>
      </div>

      <Tabs defaultValue="platform" value={activeTab} onValueChange={setActiveTab} className="px-6">
        <TabsList className="grid w-full grid-cols-3 mb-6">
          <TabsTrigger value="platform">Platform</TabsTrigger>
          <TabsTrigger value="region">Region</TabsTrigger>
          <TabsTrigger value="experience">Experience</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-0">
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={renderCustomizedLabel}
                  outerRadius={90}
                  innerRadius={40}
                  fill="#8884d8"
                  dataKey="value"
                  animationBegin={0}
                  animationDuration={1500}
                  animationEasing="ease-out"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1F2937",
                    borderColor: "#374151",
                    borderRadius: "0.5rem",
                    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                    color: "#F9FAFB",
                  }}
                  formatter={(value: number) => [`${value} contributors`, null]}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  iconType="circle"
                  layout="horizontal"
                  wrapperStyle={{ paddingTop: "10px" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </TabsContent>
      </Tabs>
    </motion.div>
  )
}

