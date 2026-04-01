import os
from dotenv import load_dotenv


load_dotenv()


def get_supabase_config():
    # add what is needed here: set your Supabase project URL
    supabase_url = os.getenv("SUPABASE_URL", "")
    # add what is needed here: set your Supabase API key
    supabase_api_key = os.getenv("SUPABASE_KEY", "")
    # add what is needed here: set your Supabase bucket name
    bucket_name = os.getenv("BUCKET_NAME", "")
    return supabase_url, supabase_api_key, bucket_name

