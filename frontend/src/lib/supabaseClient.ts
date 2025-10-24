import { createClient } from '@supabase/supabase-js'


const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || "";
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_KEY || "";

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase configuration. Please set VITE_SUPABASE_URL and VITE_SUPABASE_KEY environment variables.');
}


export const supabase = createClient(supabaseUrl, supabaseAnonKey)
