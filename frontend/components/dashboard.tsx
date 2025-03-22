"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import Sidebar from "./sidebar"
import MetricsCards from "./metrics-cards"
import CommunityEngagement from "./community-engagement"
import ContributorDistribution from "./contributor-distribution"
import Header from "./header"
import TimeFilter from "./time-filter"
import RecentActivity from "./recent-activity"
import AIInsights from "./ai-insights"
import UpcomingEvents from "./upcoming-events"
import TopContributors from "./top-contributors"

export default function Dashboard() {
  const [timeFilter, setTimeFilter] = useState<"day" | "week" | "month">("day")
  const [activeSection, setActiveSection] = useState("dashboard")

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden font-outfit">
      <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex justify-between items-center mb-8"
          >
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 text-transparent bg-clip-text">
                WELCOME TO DEVR
              </h1>
              <p className="text-gray-400 mt-2">
                Your AI-powered Developer Relations assistant is actively monitoring your open-source communities.
              </p>
            </div>
            <TimeFilter selected={timeFilter} onChange={setTimeFilter} />
          </motion.div>

          <MetricsCards timeFilter={timeFilter} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <CommunityEngagement timeFilter={timeFilter} />
            <ContributorDistribution timeFilter={timeFilter} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <RecentActivity />
            <AIInsights />
            <div className="space-y-6">
              <TopContributors />
              <UpcomingEvents />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

