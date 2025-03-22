"use client"
import { motion } from "framer-motion"
import { ArrowUpIcon, ArrowDownIcon, Users, GitPullRequest, AlertCircle, MessageSquare } from "lucide-react"
import { cn } from "@/lib/utils"

interface MetricsCardsProps {
  timeFilter: "day" | "week" | "month"
}

export default function MetricsCards({ timeFilter }: MetricsCardsProps) {
  // Dynamic data based on time filter
  const getMetrics = () => {
    if (timeFilter === "day") {
      return [
        {
          title: "Active Contributors",
          value: 235,
          change: 12,
          trend: "up",
          color: "cyan",
          icon: Users,
        },
        {
          title: "Open Issues",
          value: 72,
          change: 8,
          trend: "down",
          color: "amber",
          icon: AlertCircle,
        },
        {
          title: "Pull Requests",
          value: 52,
          change: 24,
          trend: "up",
          color: "purple",
          icon: GitPullRequest,
        },
        {
          title: "AI Interactions",
          value: 3230,
          change: 42,
          trend: "up",
          color: "blue",
          icon: MessageSquare,
        },
      ]
    } else if (timeFilter === "week") {
      return [
        {
          title: "Active Contributors",
          value: 287,
          change: 15,
          trend: "up",
          color: "cyan",
          icon: Users,
        },
        {
          title: "Open Issues",
          value: 95,
          change: 3,
          trend: "up",
          color: "amber",
          icon: AlertCircle,
        },
        {
          title: "Pull Requests",
          value: 78,
          change: 18,
          trend: "up",
          color: "purple",
          icon: GitPullRequest,
        },
        {
          title: "AI Interactions",
          value: 12450,
          change: 35,
          trend: "up",
          color: "blue",
          icon: MessageSquare,
        },
      ]
    } else {
      return [
        {
          title: "Active Contributors",
          value: 412,
          change: 22,
          trend: "up",
          color: "cyan",
          icon: Users,
        },
        {
          title: "Open Issues",
          value: 124,
          change: 5,
          trend: "down",
          color: "amber",
          icon: AlertCircle,
        },
        {
          title: "Pull Requests",
          value: 187,
          change: 32,
          trend: "up",
          color: "purple",
          icon: GitPullRequest,
        },
        {
          title: "AI Interactions",
          value: 28750,
          change: 48,
          trend: "up",
          color: "blue",
          icon: MessageSquare,
        },
      ]
    }
  }

  const metrics = getMetrics()

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const item = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 },
  }

  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      variants={container}
      initial="hidden"
      animate="show"
    >
      {metrics.map((metric, index) => (
        <motion.div
          key={index}
          variants={item}
          whileHover={{ y: -5, transition: { duration: 0.2 } }}
          className="bg-gray-900/50 backdrop-blur-sm rounded-xl p-6 border border-gray-800 hover:border-gray-700 transition-colors shadow-lg shadow-black/20"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400 font-medium">{metric.title}</h3>
            <div
              className={cn(
                "h-10 w-10 rounded-full flex items-center justify-center",
                metric.color === "cyan" && "bg-cyan-900/30 text-cyan-400",
                metric.color === "amber" && "bg-amber-900/30 text-amber-400",
                metric.color === "purple" && "bg-purple-900/30 text-purple-400",
                metric.color === "blue" && "bg-blue-900/30 text-blue-400",
              )}
            >
              <metric.icon className="h-5 w-5" />
            </div>
          </div>

          <div className="flex items-end justify-between">
            <motion.p
              className={cn(
                "text-4xl font-bold",
                metric.color === "cyan" && "text-cyan-400",
                metric.color === "amber" && "text-amber-400",
                metric.color === "purple" && "text-purple-400",
                metric.color === "blue" && "text-blue-400",
              )}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              key={metric.value} // Force animation when value changes
              transition={{ type: "spring", stiffness: 100 }}
            >
              {metric.value.toLocaleString()}
            </motion.p>
            <div
              className={cn(
                "flex items-center text-sm font-medium",
                metric.trend === "up" ? "text-green-500" : "text-red-500",
              )}
            >
              {metric.trend === "up" ? (
                <ArrowUpIcon className="h-4 w-4 mr-1" />
              ) : (
                <ArrowDownIcon className="h-4 w-4 mr-1" />
              )}
              <span>
                {metric.trend === "up" ? "+" : "-"}
                {metric.change}% from last {timeFilter}
              </span>
            </div>
          </div>

          <div className="mt-4 h-2 bg-gray-800 rounded-full overflow-hidden">
            <motion.div
              className={cn(
                "h-full rounded-full",
                metric.color === "cyan" && "bg-gradient-to-r from-cyan-500 to-cyan-400",
                metric.color === "amber" && "bg-gradient-to-r from-amber-500 to-amber-400",
                metric.color === "purple" && "bg-gradient-to-r from-purple-500 to-purple-400",
                metric.color === "blue" && "bg-gradient-to-r from-blue-500 to-blue-400",
              )}
              initial={{ width: 0 }}
              animate={{
                width: `${Math.min(100, metric.value / (timeFilter === "day" ? 10 : timeFilter === "week" ? 5 : 3))}%`,
              }}
              transition={{ duration: 1, ease: "easeOut" }}
            ></motion.div>
          </div>
        </motion.div>
      ))}
    </motion.div>
  )
}

