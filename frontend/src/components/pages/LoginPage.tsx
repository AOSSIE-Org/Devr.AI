import { useState, ReactNode, FormEvent } from "react";
import { motion } from "framer-motion";
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from "react-hot-toast";
import { supabase } from "../../lib/supabaseClient";
import {
  Settings,
  Mail,
  Lock,
  LogIn
} from 'lucide-react';

interface AuthLayoutProps {
  children: ReactNode;
}

interface InputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon: React.ElementType;
}

interface LoginPageProps {
  onLogin: () => void;
}

const AuthLayout = ({ children }: AuthLayoutProps) => (
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

const InputField = ({ icon: Icon, ...props }: InputFieldProps) => (
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

export default function LoginPage({ onLogin }: LoginPageProps) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleLogin = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    setIsLoading(true);
    const {data,error} = await supabase.auth.signInWithPassword({
      email: email,
      password: password,
    });
    setIsLoading(false);
    if(data && !error){
      toast.success('Successfully logged in!');
      onLogin();
      const rawReturn = searchParams.get('returnUrl');
      try {
        const decoded = rawReturn ? decodeURIComponent(rawReturn) : null;
        // Protect against open redirects by only allowing internal paths
        // More strict validation to prevent protocol-relative URLs and other bypasses
        if (decoded && 
            decoded.startsWith('/') && 
            !decoded.startsWith('//') && 
            !decoded.includes('\\') &&
            !decoded.includes('..') &&
            !decoded.includes('%') &&
            /^[\/a-zA-Z0-9\-_?=&]+$/.test(decoded)) {
          navigate(decoded, { replace: true });
        } else {
          navigate('/', { replace: true });
        }
      } catch (e) {
        // If decoding fails, fallback to home
        navigate('/', { replace: true });
      }
    }
    else
    {
        toast.error(error?.message ||"An Unknown error occured!");
    }
  };

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
              name="email"
              placeholder="Email address"
              required
            />
            <InputField
              icon={Lock}
              type="password"
              name="password"
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
              onClick={() => navigate('/forgot-password')}
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
}
