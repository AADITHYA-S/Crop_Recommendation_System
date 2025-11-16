// import { createClient } from '@supabase/supabase-js';
import { SUPABASE_URL, SUPABASE_ANON_KEY } from './config.js';

console.log("Supabase URL:", SUPABASE_URL);
console.log("Supabase Key:", SUPABASE_ANON_KEY);

const {createClient}=window.supabase;
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    storageKey: "cropwise_frontend_auth"
  }
});

