"use client"

import { motion } from "framer-motion"
import { GitPullRequest, GitMerge, AlertCircle, MessageSquare, User } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"

const activities = [
  {
    id: 1,
    type: "pull-request",
    title: "Fix documentation typos",
    user: "Sarah Chen",
    time: "10 minutes ago",
    status: "open",
  },
  {
    id: 2,
    type: "merge",
    title: "Add new API endpoints",
    user: "Miguel Rodriguez",
    time: "45 minutes ago",
    status: "merged",
  },
  {
    id: 3,
    type: "issue",
    title: "Bug in authentication flow",
    user: "Alex Johnson",
    time: "2 hours ago",
    status: "open",
  },
  {
    id: 4,
    type: "message",
    title: "Question about installation",
    user: "Priya Patel",
    time: "3 hours ago",
    platform: "Discord",
  },
  {
    id: 5,
    type: "pull-request",
    title: "Implement new feature",
    user: "Jordan Lee",
    time: "5 hours ago",
    status: "open",
  },
  {
    id: 6,
    type: "message",
    title: "Feedback on latest release",
    user: "Taylor Smith",
    time: "8 hours ago",
    platform: "Slack",
  },
]

export default function RecentActivity() {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case "pull-request":
        return <GitPullRequest className="h-4 w-4 text-blue-500" />
      case "merge":
        return <GitMerge className="h-4 w-4 text-purple-500" />
      case "issue":
        return <AlertCircle className="h-4 w-4 text-amber-500" />
      case "message":
        return <MessageSquare className="h-4 w-4 text-green-500" />
      default:
        return null
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "open":
        return <Badge className="bg-blue-900/50 text-blue-400 hover:bg-blue-900 border-blue-700">Open</Badge>
      case "merged":
        return <Badge className="bg-purple-900/50 text-purple-400 hover:bg-purple-900 border-purple-700">Merged</Badge>
      case "closed":
        return <Badge className="bg-red-900/50 text-red-400 hover:bg-red-900 border-red-700">Closed</Badge>
      default:
        return null
    }
  }

  const getPlatformBadge = (platform: string) => {
    switch (platform) {
      case "Discord":
        return <Badge className="bg-purple-900/50 text-purple-400 hover:bg-purple-900 border-purple-700">Discord</Badge>
      case "Slack":
        return <Badge className="bg-amber-900/50 text-amber-400 hover:bg-amber-900 border-amber-700">Slack</Badge>
      default:
        return null
    }
  }

  return (
    <motion.div
      className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 shadow-lg shadow-black/20 overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <div className="p-6 border-b border-gray-800">
        <h2 className="text-xl font-semibold">Recent Activity</h2>
      </div>

      <ScrollArea className="h-[400px]">
        <div className="p-4 space-y-3">
          {activities.map((activity, index) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
              className="flex items-start space-x-4 p-3 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-gray-600 transition-all cursor-pointer"
            >
              <div className="h-10 w-10 rounded-full bg-gray-700 flex items-center justify-center">
                <User className="h-5 w-5 text-gray-300" />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center">
                  {getActivityIcon(activity.type)}
                  <span className="ml-2 text-sm font-medium truncate">{activity.title}</span>
                </div>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs text-gray-400 truncate">
                    {activity.user} • {activity.time}
                  </span>
                  <div className="flex space-x-2">
                    {activity.status && getStatusBadge(activity.status)}
                    {activity.platform && getPlatformBadge(activity.platform)}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </ScrollArea>
    </motion.div>
  )
}

