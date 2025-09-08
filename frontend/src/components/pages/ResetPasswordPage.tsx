import { useState, useEffect } from "react";
import type { ReactNode, FormEvent } from "react";
import { motion } from "framer-motion";
import { useNavigate } from 'react-router-dom';
import { toast} from "react-hot-toast";
import { supabase } from "../../lib/supabaseClient";
import {
  Settings,
  Lock,
  Key
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




export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState<boolean>(false);


  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));

    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');

    const clearUrlHash = () => {
      if (window.location.hash) {
        window.history.replaceState({}, document.title, window.location.pathname + window.location.search);
      }
    };

    if (accessToken && refreshToken) {
      (async () => {
        try {
          const { error } = await supabase.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
          });
          if (error) {
            toast.error("Error setting session: " + error.message);
            navigate('/login', { replace: true });
          }
        } catch {
          toast.error("Error setting session");
          navigate('/login', { replace: true });
        } finally {
          clearUrlHash();
        }
      })();
    } else {
      toast.error("Access denied");
      navigate('/login', { replace: true });
      clearUrlHash();
    }
  }, [navigate]);


  const handleAuth = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const password = formData.get('password-1') as string;
    const repassword = formData.get('password-2') as string;
    if (password != repassword) {
      toast.error("Passwords doesn't match. Try Again");
      return;
    }
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters long.");
      return;
    }
    if (!/[A-Z]/.test(password)) {
      toast.error("Password must contain at least one uppercase letter.");
      return;
    }
    if (!/[a-z]/.test(password)) {
      toast.error("Password must contain at least one lowercase letter.");
      return;
    }
    if (!/[0-9]/.test(password)) {
      toast.error("Password must contain at least one number.");
      return;
    }
    if (!/[^A-Za-z0-9]/.test(password)) {
      toast.error("Password must contain at least one special character.");
      return;
    }
    setIsLoading(true);
    try {
      const { error } = await supabase.auth.updateUser({ password });
      if (error) {
        toast.error(error.message || "An unknown error occurred!");
        return;
      }
      toast.success("Password updated successfully.");
      navigate("/");
    } catch {
      toast.error("Unexpected error updating password.");
    } finally {
      setIsLoading(false);
    }
  }
  return (
    <AuthLayout>
      <div className="bg-gray-900 p-8 rounded-xl border border-gray-800">
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
              icon={Key}
              type="password"
              name="password-1"
              className="mb-7"
              placeholder="New Password"
              required
            />
            <InputField
              icon={Key}
              type="password"
              name="password-2"
              className="mb-7"
              placeholder="Reenter Password"
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
      </div>
    </AuthLayout>
  );
}
