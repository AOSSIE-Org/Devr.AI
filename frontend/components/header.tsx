"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Bell, HelpCircle, Search, X, User, LogOut, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"

export default function Header() {
  const [searchOpen, setSearchOpen] = useState(false)

  return (
    <header className="bg-gray-900/80 backdrop-blur-md border-b border-gray-800 py-3 px-6 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center">
        {!searchOpen ? (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSearchOpen(true)}
            className="text-gray-400 hover:text-cyan-400 hover:bg-gray-800 mr-2"
          >
            <Search className="h-5 w-5" />
          </Button>
        ) : (
          <AnimatePresence>
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 300, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="flex items-center bg-gray-800 rounded-md px-3 py-1.5 relative"
            >
              <Search className="h-4 w-4 text-gray-400 mr-2" />
              <Input
                type="text"
                placeholder="Search projects, issues, PRs..."
                className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 h-7 p-0 text-sm"
                autoFocus
              />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSearchOpen(false)}
                className="h-6 w-6 p-0 text-gray-400 hover:text-white absolute right-2"
              >
                <X className="h-4 w-4" />
              </Button>
            </motion.div>
          </AnimatePresence>
        )}
      </div>

      <div className="flex items-center space-x-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="relative text-gray-400 hover:text-cyan-400 hover:bg-gray-800"
            >
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-cyan-500 text-xs flex items-center justify-center text-white">
                3
              </span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <DropdownMenuLabel>Notifications</DropdownMenuLabel>
            <DropdownMenuSeparator />

            <div className="max-h-[300px] overflow-y-auto">
              {[1, 2, 3].map((i) => (
                <DropdownMenuItem key={i} className="flex flex-col items-start p-3 cursor-pointer">
                  <div className="flex items-center w-full">
                    <div className="h-8 w-8 rounded-full bg-cyan-900 flex items-center justify-center mr-2">
                      <User className="h-4 w-4 text-cyan-400" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">New contributor joined</p>
                      <p className="text-xs text-gray-400">User123 made their first contribution</p>
                    </div>
                    <span className="text-xs text-gray-400 whitespace-nowrap">{i * 10}m ago</span>
                  </div>
                </DropdownMenuItem>
              ))}
            </div>

            <DropdownMenuSeparator />
            <DropdownMenuItem className="justify-center">
              <Button variant="ghost" size="sm" className="text-cyan-400 hover:text-cyan-300 w-full">
                View all notifications
              </Button>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Badge className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 border-0 py-1 px-3">
            Beta
          </Badge>
        </motion.div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="text-gray-400 hover:text-cyan-400 hover:bg-gray-800">
              <HelpCircle className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Documentation</DropdownMenuItem>
            <DropdownMenuItem>API Reference</DropdownMenuItem>
            <DropdownMenuItem>Community Support</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Contact Us</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="gap-2 text-gray-300 hover:text-white hover:bg-gray-800">
              <div className="h-6 w-6 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                <span className="text-white font-bold text-xs">A</span>
              </div>
              <span className="hidden md:inline">Admin</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" />
              <span>Profile</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2 h-4 w-4" />
              <span>Settings</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-red-500">
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}

