"use client"

import { motion } from "framer-motion"
import { Brain, Lightbulb, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"

const insights = [
  {
    icon: TrendingUp,
    title: "Contributor Growth",
    description: "New contributor onboarding has increased by 28% since implementing AI-assisted documentation.",
    color: "cyan",
  },
  {
    icon: Lightbulb,
    title: "Issue Resolution",
    description: "Average time to first response on issues has decreased by 45% with automated triage.",
    color: "amber",
  },
  {
    icon: Brain,
    title: "Knowledge Sharing",
    description: "AI has answered 1,245 community questions this month with a 92% satisfaction rate.",
    color: "purple",
  },
  {
    icon: AlertTriangle,
    title: "Potential Bottleneck",
    description:
      "Pull request review times are increasing. Consider adding more reviewers to the authentication module.",
    color: "red",
  },
  {
    icon: CheckCircle,
    title: "Documentation Impact",
    description: "Updated API documentation has reduced related support questions by 37% this month.",
    color: "green",
  },
]

export default function AIInsights() {
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
    hidden: { opacity: 0, x: -20 },
    show: { opacity: 1, x: 0 },
  }

  return (
    <motion.div
      className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 shadow-lg shadow-black/20 overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center">
          <Brain className="h-5 w-5 text-cyan-400 mr-2" />
          <h2 className="text-xl font-semibold">AI-Generated Insights</h2>
        </div>
      </div>

      <ScrollArea className="h-[400px]">
        <motion.div className="p-4 space-y-4" variants={container} initial="hidden" animate="show">
          {insights.map((insight, index) => (
            <motion.div
              key={index}
              className="p-4 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-gray-600 transition-all"
              variants={item}
              whileHover={{ y: -2, transition: { duration: 0.2 } }}
            >
              <div className="flex">
                <div
                  className={`h-10 w-10 rounded-full flex items-center justify-center mr-4 
                  ${
                    insight.color === "cyan"
                      ? "bg-cyan-900/30 text-cyan-400"
                      : insight.color === "amber"
                        ? "bg-amber-900/30 text-amber-400"
                        : insight.color === "purple"
                          ? "bg-purple-900/30 text-purple-400"
                          : insight.color === "red"
                            ? "bg-red-900/30 text-red-400"
                            : "bg-green-900/30 text-green-400"
                  }`}
                >
                  <insight.icon className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-medium text-white">{insight.title}</h3>
                  <p className="text-gray-400 text-sm mt-1">{insight.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </ScrollArea>
    </motion.div>
  )
}

