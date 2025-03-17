import React, { useState } from "react";
import { motion } from "framer-motion";
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { toast } from "react-hot-toast";
import { 
    LayoutDashboard, 
    Bot, 
    Github, 
    MessageSquare, 
    Slack,
    Users,
    Activity,
    GitPullRequest,
    MessageCircleQuestion,
    Menu,
    ChevronRight,
    Settings,
    Shield,
    KeyRound,
    Mail,
    Lock,
    User,
    LogIn,
    UserPlus
  } from 'lucide-react';

export default function LoginPage  () {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
  
    const handleLogin = async (e:any) => {
      e.preventDefault();
      setIsLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setIsLoading(false);
      toast.success('Successfully logged in!');
      navigate('/');
    };
    const AuthLayout = ({ children }:any) => (
        <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full max-w-md"
          >
            {children}
          </motion.div>
        </div>
      );
      
      const InputField = ({ icon: Icon, ...props }:any) => (
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            {...props}
            className="block w-full pl-10 pr-3 py-2 border border-gray-800 rounded-lg bg-gray-900 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
      );
      
  
    return (
      <AuthLayout>
        <div className="bg-gray-900 p-8 rounded-xl border border-gray-800">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center mb-8"
          >
            <h1 className="text-3xl font-bold text-white mb-2">Welcome back</h1>
            <p className="text-gray-400">Sign in to your account</p>
          </motion.div>
  
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-4">
              <InputField
                icon={Mail}
                type="email"
                placeholder="Email address"
                required
              />
              <InputField
                icon={Lock}
                type="password"
                placeholder="Password"
                required
              />
            </div>
  
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center">
                <input type="checkbox" className="rounded bg-gray-800 border-gray-700 text-green-500 focus:ring-green-500" />
                <span className="ml-2 text-gray-300">Remember me</span>
              </label>
              <button
                type="button"
                onClick={() => toast.success('Reset link sent!')}
                className="text-green-400 hover:text-green-300"
              >
                Forgot password?
              </button>
            </div>
  
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center"
            >
              {isLoading ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <Settings size={20} />
                </motion.div>
              ) : (
                <>
                  <LogIn size={20} className="mr-2" />
                  Sign In
                </>
              )}
            </motion.button>
  
            <p className="text-center text-gray-400 text-sm">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => navigate('/signup')}
                className="text-green-400 hover:text-green-300 font-medium"
              >
                Sign up
              </button>
            </p>
          </form>
        </div>
      </AuthLayout>
    );
  };
  



