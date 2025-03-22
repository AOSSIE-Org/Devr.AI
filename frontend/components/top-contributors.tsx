"use client"

import { motion } from "framer-motion"
import { Award, Github, MessageSquare } from "lucide-react"

const contributors = [
  {
    name: "Sarah Chen",
    contributions: 42,
    platform: "github",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    name: "Miguel Rodriguez",
    contributions: 38,
    platform: "github",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    name: "Priya Patel",
    contributions: 35,
    platform: "discord",
    avatar: "/placeholder.svg?height=40&width=40",
  },
]

export default function TopContributors() {
  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case "github":
        return <Github className="h-4 w-4 text-gray-400" />
      case "discord":
      case "slack":
        return <MessageSquare className="h-4 w-4 text-gray-400" />
      default:
        return null
    }
  }

  return (
    <motion.div
      className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 shadow-lg shadow-black/20 overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
    >
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center">
          <Award className="h-5 w-5 text-amber-400 mr-2" />
          <h2 className="text-lg font-semibold">Top Contributors</h2>
        </div>
      </div>

      <div className="p-4 space-y-3">
        {contributors.map((contributor, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 + 0.2 }}
            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
            className="flex items-center p-2 rounded-lg hover:bg-gray-800/50 transition-colors cursor-pointer"
          >
            <div className="relative">
              <img
                src={contributor.avatar || "/placeholder.svg"}
                alt={contributor.name}
                className="h-10 w-10 rounded-full"
              />
              <div className="absolute -bottom-1 -right-1 h-5 w-5 rounded-full bg-gray-800 flex items-center justify-center">
                {getPlatformIcon(contributor.platform)}
              </div>
            </div>

            <div className="ml-3 flex-1">
              <p className="font-medium">{contributor.name}</p>
              <p className="text-xs text-gray-400">{contributor.contributions} contributions</p>
            </div>

            <div
              className={`h-8 w-8 rounded-full flex items-center justify-center 
              ${
                index === 0
                  ? "bg-amber-900/30 text-amber-400"
                  : index === 1
                    ? "bg-gray-700/50 text-gray-300"
                    : "bg-orange-900/30 text-orange-400"
              }`}
            >
              {index + 1}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

