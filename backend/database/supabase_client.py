from supabase import create_client,client
import os

supabase_url=os.getenv("SUPABASE_URL")
supabase_key=os.getenv("SUPABASE_ROLE_KEY")
supabase:client=create_client(supabase_url,supabase_key)