"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface TimeFilterProps {
  selected: "day" | "week" | "month"
  onChange: (value: "day" | "week" | "month") => void
}

export default function TimeFilter({ selected, onChange }: TimeFilterProps) {
  const options: ("day" | "week" | "month")[] = ["day", "week", "month"]

  return (
    <div className="bg-gray-900 rounded-full p-1 flex shadow-lg shadow-black/20">
      {options.map((option) => (
        <div key={option} className="relative">
          {selected === option && (
            <motion.div
              layoutId="timeFilterBackground"
              className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-600/20 rounded-full"
              transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
            />
          )}
          <button
            onClick={() => onChange(option)}
            className={cn(
              "relative z-10 px-4 py-1.5 rounded-full text-sm font-medium transition-colors capitalize",
              selected === option ? "text-white" : "text-gray-400 hover:text-white",
            )}
          >
            {option}
          </button>
        </div>
      ))}
    </div>
  )
}

