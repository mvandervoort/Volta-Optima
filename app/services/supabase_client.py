import os
import logging
from supabase import create_client, Client

supabase: Client = None
try:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key:
        supabase = create_client(url, key)
    else:
        logging.warning(
            "SUPABASE_URL or SUPABASE_KEY environment variables are missing. Supabase client will be None."
        )
except Exception as e:
    logging.exception(f"Error initializing Supabase client: {e}")