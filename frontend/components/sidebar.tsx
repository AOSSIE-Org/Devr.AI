"use client"

import type React from "react"

import { useState } from "react"
import { motion } from "framer-motion"
import {
  BarChart2,
  GitPullRequest,
  Github,
  MessageSquare,
  Users,
  Bot,
  BookOpen,
  Slack,
  Settings,
  LayoutDashboard,
  ChevronLeft,
  ChevronRight,
  Bell,
  Calendar,
  Code,
  HelpCircle,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface SidebarProps {
  activeSection: string
  setActiveSection: (section: string) => void
}

interface NavItem {
  id: string
  name: string
  icon: React.ElementType
  badge?: number
}

interface NavSection {
  title: string
  items: NavItem[]
}

export default function Sidebar({ activeSection, setActiveSection }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false)

  const navSections: NavSection[] = [
    {
      title: "Dashboard",
      items: [
        { id: "dashboard", name: "Overview", icon: LayoutDashboard },
        { id: "contributors", name: "Contributors", icon: Users, badge: 5 },
        { id: "pull-requests", name: "Pull Requests", icon: GitPullRequest, badge: 12 },
        { id: "community", name: "Community", icon: MessageSquare },
      ],
    },
    {
      title: "AI Tools",
      items: [
        { id: "ai-assistant", name: "AI Assistant", icon: Bot },
        { id: "knowledge-base", name: "Knowledge Base", icon: BookOpen },
        { id: "analytics", name: "Analytics", icon: BarChart2 },
        { id: "notifications", name: "Notifications", icon: Bell, badge: 3 },
      ],
    },
    {
      title: "Integrations",
      items: [
        { id: "github", name: "GitHub", icon: Github },
        { id: "discord", name: "Discord", icon: MessageSquare },
        { id: "slack", name: "Slack", icon: Slack },
        { id: "events", name: "Events", icon: Calendar },
      ],
    },
    {
      title: "Development",
      items: [
        { id: "code", name: "Code Snippets", icon: Code },
        { id: "help", name: "Help & Support", icon: HelpCircle },
        { id: "settings", name: "Settings", icon: Settings },
      ],
    },
  ]

  return (
    <motion.div
      className="bg-gray-900 border-r border-gray-800 flex flex-col h-full relative"
      animate={{ width: collapsed ? 80 : 260 }}
      transition={{ duration: 0.3 }}
    >
      <div className="p-4 border-b border-gray-800 flex items-center justify-between">
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="flex items-center"
          >
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center mr-3 shadow-lg shadow-cyan-500/20">
              <span className="text-white font-bold text-xl">D</span>
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 text-transparent bg-clip-text">
              Devr.AI
            </h1>
          </motion.div>
        )}

        {collapsed && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mx-auto">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <span className="text-white font-bold text-xl">D</span>
            </div>
          </motion.div>
        )}

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-gray-400 hover:text-cyan-400 transition-colors p-1 rounded-full hover:bg-gray-800"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-4 scrollbar-thin scrollbar-thumb-gray-800">
        {navSections.map((section, sectionIndex) => (
          <div key={sectionIndex} className="mb-6">
            {!collapsed && (
              <h2 className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                {section.title}
              </h2>
            )}
            <ul>
              {section.items.map((item) => (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveSection(item.id)}
                    className={cn(
                      "w-full flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-cyan-400 transition-all duration-200",
                      activeSection === item.id && "bg-gray-800 text-cyan-400 border-l-2 border-cyan-400",
                      collapsed && "justify-center px-0",
                    )}
                  >
                    <motion.div whileHover={{ scale: 1.1 }} className={cn("relative", collapsed && "mx-auto")}>
                      <item.icon className="h-5 w-5" />
                      {item.badge && (
                        <span className="absolute -top-2 -right-2 h-4 w-4 rounded-full bg-cyan-500 text-xs flex items-center justify-center text-white">
                          {item.badge}
                        </span>
                      )}
                    </motion.div>

                    {!collapsed && <span className="ml-3">{item.name}</span>}

                    {!collapsed && item.badge && (
                      <span className="ml-auto bg-gray-700 text-xs py-1 px-2 rounded-full">{item.badge}</span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-gray-800">
        {!collapsed ? (
          <div className="flex items-center">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center mr-3">
              <span className="text-white font-bold">A</span>
            </div>
            <div>
              <p className="font-medium">Admin</p>
              <p className="text-sm text-gray-400">admin@devr.ai</p>
            </div>
            <button className="ml-auto text-gray-400 hover:text-cyan-400 p-1 rounded-full hover:bg-gray-800">
              <Settings className="h-5 w-5" />
            </button>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
              <span className="text-white font-bold">A</span>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}

