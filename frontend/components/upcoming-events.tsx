"use client"

import { motion } from "framer-motion"
import { Calendar, Clock } from "lucide-react"

const events = [
  {
    title: "Community Call",
    date: "Tomorrow",
    time: "3:00 PM",
    type: "virtual",
  },
  {
    title: "Hackathon Kickoff",
    date: "Mar 20",
    time: "10:00 AM",
    type: "virtual",
  },
  {
    title: "Release Planning",
    date: "Mar 25",
    time: "2:00 PM",
    type: "virtual",
  },
]

export default function UpcomingEvents() {
  return (
    <motion.div
      className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 shadow-lg shadow-black/20 overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.7 }}
    >
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center">
          <Calendar className="h-5 w-5 text-blue-400 mr-2" />
          <h2 className="text-lg font-semibold">Upcoming Events</h2>
        </div>
      </div>

      <div className="p-4 space-y-3">
        {events.map((event, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 + 0.2 }}
            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
            className="p-3 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-gray-600 transition-all cursor-pointer"
          >
            <h3 className="font-medium">{event.title}</h3>
            <div className="flex items-center mt-2 text-sm text-gray-400">
              <Calendar className="h-4 w-4 mr-1" />
              <span>{event.date}</span>
              <span className="mx-2">•</span>
              <Clock className="h-4 w-4 mr-1" />
              <span>{event.time}</span>
              <span className="ml-auto px-2 py-0.5 rounded-full text-xs bg-blue-900/30 text-blue-400 border border-blue-800">
                {event.type}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

