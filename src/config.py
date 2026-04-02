import os
from dotenv import load_dotenv


load_dotenv()


def get_supabase_config():
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_api_key = os.getenv("SUPABASE_KEY", "")
    bucket_name = os.getenv("BUCKET_NAME", "")
    return supabase_url, supabase_api_key, bucket_name

