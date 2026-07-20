import os
import requests
import logging
from config import settings

logger = logging.getLogger("ats-optimizer")

def upload_file_to_supabase(file_bytes: bytes, filename: str) -> str:
    """
    Uploads a file directly to a Supabase storage bucket via REST API.
    If upload succeeds, returns public URL. Otherwise, returns filename representation.
    """
    supabase_url = settings.SUPABASE_URL
    supabase_key = settings.SUPABASE_KEY
    bucket_name = settings.SUPABASE_BUCKET_NAME

    if not supabase_url or not supabase_key:
        logger.warning("Supabase URL or Key is not configured. Falling back to local filepath representation.")
        return filename

    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    upload_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{safe_filename}"

    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "apikey": supabase_key
    }

    try:
        logger.info(f"Attempting to upload {safe_filename} to Supabase storage bucket: {bucket_name}...")
        response = requests.post(upload_url, headers=headers, data=file_bytes)

        if response.status_code == 400 and ("The resource already exists" in response.text or "Duplicate" in response.text):
            logger.info(f"File {safe_filename} already exists. Attempting overwrite (PUT)...")
            response = requests.put(upload_url, headers=headers, data=file_bytes)

        if response.status_code == 200:
            logger.info(f"Successfully uploaded {safe_filename} to Supabase Storage.")
            return f"{supabase_url}/storage/v1/object/public/{bucket_name}/{safe_filename}"
        else:
            logger.error(f"Failed to upload to Supabase Storage: {response.status_code} - {response.text}")
            return filename

    except Exception as e:
        logger.error(f"Error uploading file to Supabase Storage: {e}")
        return filename
