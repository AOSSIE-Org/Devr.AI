import { useState, ReactNode, FormEvent } from "react";
import { motion } from "framer-motion";
import { useNavigate } from 'react-router-dom';
import { toast, Toaster } from "react-hot-toast";
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


export default function SignUpPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [mailPage, setMailPage] = useState<boolean>(false);

  const handleSignUp = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const email = formData.get('email') as string;
    const name = formData.get('name') as string;
    const password = formData.get('password-1') as string;
    const repassword = formData.get('password-2') as string;

    if (password != repassword) {
      toast.error("Passwords doesn't match.Try Again");
      return;
    }
    setIsLoading(true);
    const { data, error } = await supabase.auth.signUp({
      email: email,
      password: password,
      options: {
        data: {
          display_name: name
        },
        emailRedirectTo: 'http://localhost:5173/',
      },
    })
    setIsLoading(false);
    // Email already confirmed
    if (data?.user?.confirmed_at) {
      toast.error("Email is already registered. Please log in.");
      return;
    }
    if (error) {
      toast.error(error.message || "An Unknown error occured!");
      return;
    }
    setMailPage(true);
  };

  return (
    <AuthLayout>

      <div className="bg-gray-900 p-8 rounded-xl border border-gray-800">
        <Toaster position="top-right" />
        {!mailPage ? (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center mb-8"
            >
              <h1 className="text-3xl font-bold text-white mb-2">Welcome to Devr.AI</h1>
              <p className="text-gray-400">Create a new account</p>
            </motion.div>
            <form onSubmit={handleSignUp} className="space-y-6">
              <div className="space-y-4">
                <InputField
                  icon={Mail}
                  name="name"
                  placeholder="Username"
                  required
                />
                <InputField
                  icon={Mail}
                  type="email"
                  name="email"
                  placeholder="Email address"
                  required
                />
                <InputField
                  icon={Lock}
                  type="password-1"
                  name="password"
                  placeholder="Password"
                  required
                />
                <InputField
                  icon={Lock}
                  type="password"
                  name="password-2"
                  placeholder="Reenter Password"
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
                    Sign Up
                  </>
                )}
              </motion.button>

              <p className="text-center text-gray-400 text-sm">
                Already have an Account?{' '}
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  className="text-green-400 hover:text-green-300 font-medium"
                >
                  Sign In
                </button>
              </p>
            </form>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center py-12">
            <Mail className="w-16 h-16 text-green-500 mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Check your inbox</h2>
            <p className="text-gray-400 mb-4 text-center">
              We've sent a confirmation email to your address. Please check your inbox and follow the instructions to complete your registration.
            </p>
            <button
              type="button"
              onClick={() => { setMailPage(false); navigate('/login') }}
              className="mt-4 px-6 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors"
            >
              Back to Sign In
            </button>
          </div>
        )}
      </div>
    </AuthLayout>
  );
}
