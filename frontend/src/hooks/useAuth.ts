import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';
import toast from 'react-hot-toast';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data, error }) => {
      if (error) {
        console.error('Error checking session:', error);
      }
      setIsAuthenticated(!!data?.session);
      setLoading(false);
    });

    const { data: subscription } = supabase.auth.onAuthStateChange(
      (event, _session) => {
        switch (event) {
          case "SIGNED_IN":
            setIsAuthenticated(true);
            toast.success("Signed in!");
            break;
          case "SIGNED_OUT":
            setIsAuthenticated(false);
            toast.success("Signed out!");
            break;
          default:
            break;
        }
      }
    );

    return () => {
      subscription.subscription.unsubscribe();
    };
  }, []);

  const logout = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      toast.error('Logout failed');
      return;
    }
    setIsAuthenticated(false);
  };

  return { isAuthenticated, loading, logout };
};
