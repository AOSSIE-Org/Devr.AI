import { useState, ReactNode, FormEvent } from "react";
import { motion } from "framer-motion";
import { useNavigate } from 'react-router-dom';
import { toast} from "react-hot-toast";
import { supabase } from "../../lib/supabaseClient";


import {
  Settings,
  Mail,
  Lock,
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


export default function ForgotPasswrdPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [mailPage, setMailPage] = useState<boolean>(false);

  const handleAuth = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const email = String(formData.get('email') || '').trim();
    if (!email) {
      toast.error("Please enter your email address.");
      return;
    }
    setIsLoading(true);
    try {
      const base = import.meta.env.VITE_BASE_URL || window.location.origin;
      const redirectTo = new URL('/reset-password', base).toString();
      const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo });
      if (error) {
        console.error('resetPasswordForEmail failed', error);
      }
      setMailPage(true);
    } catch (err) {
      console.error('resetPasswordForEmail unexpected error', err);
      toast.error("Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>

      <div className="bg-gray-900 p-8 rounded-xl border border-gray-800">
        {!mailPage ? (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center mb-8"
            >
              <h1 className="text-3xl font-bold text-white mb-2">Account Recovery</h1>
              <p className="text-gray-400">Reset your password</p>
            </motion.div>
            <form onSubmit={handleAuth} className="space-y-6">
              <InputField
                icon={Mail}
                type="email"
                name="email"
                className="mb-7"
                placeholder="Email address"
                required
              />
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
                    <Lock size={20} className="mr-2" />
                    Reset Password
                    </>
                )}
              </motion.button>
              <p className="text-center text-gray-400 text-sm">
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  className="text-gray-400 hover:text-gray-300 font-medium"
                >
                  Back to Sign In
                </button>
              </p>
            </form>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center py-12">
            <Mail className="w-16 h-16 text-green-500 mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Check your inbox</h2>
            <p className="text-gray-400 mb-4 text-center">
              We've sent a password reset email to this address. Please check your inbox and follow the instructions to reset your password.
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
