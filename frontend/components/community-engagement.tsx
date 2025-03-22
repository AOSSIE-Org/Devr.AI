"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

interface CommunityEngagementProps {
  timeFilter: "day" | "week" | "month"
}

export default function CommunityEngagement({ timeFilter }: CommunityEngagementProps) {
  const [activeTab, setActiveTab] = useState("activity")

  // Dynamic data based on time filter
  const getData = () => {
    if (timeFilter === "day") {
      return [
        { name: "12am", github: 15, discord: 10, slack: 5 },
        { name: "3am", github: 10, discord: 5, slack: 2 },
        { name: "6am", github: 20, discord: 12, slack: 8 },
        { name: "9am", github: 35, discord: 25, slack: 15 },
        { name: "12pm", github: 50, discord: 35, slack: 20 },
        { name: "3pm", github: 65, discord: 45, slack: 30 },
        { name: "6pm", github: 55, discord: 40, slack: 25 },
        { name: "9pm", github: 40, discord: 30, slack: 18 },
      ]
    } else if (timeFilter === "week") {
      return [
          { name: 'Mon', github: 40, discord: 24, slack: 18 },
          { name: 'Tue', github: 30, discord: 28, slack: 22 },
          { name: 'Wed', github: 45, discord: 32, slack: 25 },
          { name: 'Thu', github: 50, discord: 38, slack: 30 },
      ];
  }
   else {
      return [
        { name: "Week 1", github: 180, discord: 120, slack: 80 },
        { name: "Week 2", github: 220, discord: 150, slack: 95 },
        { name: "Week 3", github: 280, discord: 190, slack: 110 },
        { name: "Week 4", github: 350, discord: 230, slack: 140 },
      ]
    }
  }

  const getTabContent = () => {
    if (activeTab === "activity") {
      return getData()
    } else if (activeTab === "messages") {
      // Different data for messages tab
      if (timeFilter === "day") {
        return [
          { name: "12am", github: 5, discord: 25, slack: 15 },
          { name: "3am", github: 3, discord: 15, slack: 8 },
          { name: "6am", github: 8, discord: 30, slack: 20 },
          { name: "9am", github: 15, discord: 60, slack: 35 },
          { name: "12pm", github: 20, discord: 85, slack: 45 },
          { name: "3pm", github: 25, discord: 95, slack: 55 },
          { name: "6pm", github: 22, discord: 80, slack: 50 },
          { name: "9pm", github: 18, discord: 65, slack: 40 },
        ]
      } else if (timeFilter === "week") {
        return [
          { name: "Mon", github: 20, discord: 65, slack: 40 },
          { name: "Tue", github: 15, discord: 70, slack: 45 },
          { name: "Wed", github: 22, discord: 80, slack: 50 },
          { name: "Thu", github: 25, discord: 90, slack: 55 },
          { name: "Fri", github: 30, discord: 100, slack: 60 },
          { name: "Sat", github: 18, discord: 60, slack: 35 },
          { name: "Sun", github: 12, discord: 50, slack: 30 },
        ]
      } else {
        return [
          { name: "Week 1", github: 90, discord: 350, slack: 200 },
          { name: "Week 2", github: 110, discord: 420, slack: 240 },
          { name: "Week 3", github: 140, discord: 480, slack: 280 },
          { name: "Week 4", github: 175, discord: 550, slack: 320 },
        ]
      }
    } else {
      // Reactions tab
      if (timeFilter === "day") {
        return [
          { name: "12am", github: 8, discord: 18, slack: 10 },
          { name: "3am", github: 5, discord: 10, slack: 6 },
          { name: "6am", github: 12, discord: 22, slack: 14 },
          { name: "9am", github: 25, discord: 45, slack: 28 },
          { name: "12pm", github: 35, discord: 65, slack: 38 },
          { name: "3pm", github: 45, discord: 75, slack: 42 },
          { name: "6pm", github: 38, discord: 60, slack: 35 },
          { name: "9pm", github: 30, discord: 48, slack: 30 },
        ]
      } else if (timeFilter === "week") {
        return [
          { name: "Mon", github: 30, discord: 50, slack: 30 },
          { name: "Tue", github: 25, discord: 55, slack: 35 },
          { name: "Wed", github: 35, discord: 65, slack: 40 },
          { name: "Thu", github: 40, discord: 70, slack: 45 },
          { name: "Fri", github: 50, discord: 80, slack: 50 },
          { name: "Sat", github: 28, discord: 45, slack: 28 },
          { name: "Sun", github: 20, discord: 40, slack: 25 },
        ]
      } else {
        return [
          { name: "Week 1", github: 140, discord: 280, slack: 160 },
          { name: "Week 2", github: 170, discord: 340, slack: 190 },
          { name: "Week 3", github: 210, discord: 390, slack: 220 },
          { name: "Week 4", github: 260, discord: 450, slack: 250 },
        ]
      }
    }
  }

  return (
    <motion.div
      className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 shadow-lg shadow-black/20 overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-1">Community Engagement</h2>
        <p className="text-gray-400 text-sm">Daily activity across all platforms</p>
      </div>

      <Tabs defaultValue="activity" value={activeTab} onValueChange={setActiveTab} className="px-6">
        <TabsList className="grid w-full grid-cols-3 mb-6">
          <TabsTrigger value="activity">Activity</TabsTrigger>
          <TabsTrigger value="messages">Messages</TabsTrigger>
          <TabsTrigger value="reactions">Reactions</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-0">
          <div className="h-72 w-full px-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={getTabContent()} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                <XAxis dataKey="name" stroke="#9CA3AF" tick={{ fontSize: 12 }} tickLine={{ stroke: "#4B5563" }} />
                <YAxis stroke="#9CA3AF" tick={{ fontSize: 12 }} tickLine={{ stroke: "#4B5563" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1F2937",
                    borderColor: "#374151",
                    borderRadius: "0.5rem",
                    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                    color: "#F9FAFB",
                  }}
                  itemStyle={{ padding: "4px 0" }}
                  cursor={{ stroke: "#6B7280", strokeWidth: 1 }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ paddingTop: "10px" }} />
                <Line
                  type="monotone"
                  dataKey="github"
                  name="GitHub"
                  stroke="#06B6D4"
                  strokeWidth={3}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6, stroke: "#06B6D4", strokeWidth: 2, fill: "#06B6D4" }}
                  animationDuration={1500}
                  animationEasing="ease-out"
                />
                <Line
                  type="monotone"
                  dataKey="discord"
                  name="Discord"
                  stroke="#8B5CF6"
                  strokeWidth={3}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6, stroke: "#8B5CF6", strokeWidth: 2, fill: "#8B5CF6" }}
                  animationDuration={1500}
                  animationEasing="ease-out"
                  animationBegin={300}
                />
                <Line
                  type="monotone"
                  dataKey="slack"
                  name="Slack"
                  stroke="#F59E0B"
                  strokeWidth={3}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6, stroke: "#F59E0B", strokeWidth: 2, fill: "#F59E0B" }}
                  animationDuration={1500}
                  animationEasing="ease-out"
                  animationBegin={600}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </TabsContent>
      </Tabs>
    </motion.div>
  )
}

