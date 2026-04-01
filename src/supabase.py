import mimetypes
from pathlib import Path

import requests

from .config import get_supabase_config


def upload_file_to_supabase(local_file_path, remote_path):
    supabase_url, supabase_api_key, bucket_name = get_supabase_config()
    if not supabase_url or not supabase_api_key or not bucket_name:
        print("Supabase config not set. Skipping upload.")
        return

    upload_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{remote_path}"
    content_type = mimetypes.guess_type(local_file_path)[0] or "application/octet-stream"
    headers = {
        "apikey": supabase_api_key,
        "Authorization": f"Bearer {supabase_api_key}",
        "Content-Type": content_type,
        "x-upsert": "true",
    }

    with open(local_file_path, "rb") as f:
        response = requests.post(upload_url, headers=headers, data=f)

    if response.status_code in (400, 409):
        with open(local_file_path, "rb") as f:
            response = requests.put(upload_url, headers=headers, data=f)

    if response.status_code not in (200, 201):
        print(f"Failed upload: {remote_path} -> {response.status_code} {response.text}")
    else:
        print(f"Uploaded to Supabase: {remote_path}")


def upload_folder_to_supabase(local_folder, remote_prefix):
    folder = Path(local_folder)
    if not folder.exists():
        return
    for file_path in folder.rglob("*"):
        if file_path.is_file():
            remote_path = f"{remote_prefix}/{file_path.relative_to(folder).as_posix()}"
            upload_file_to_supabase(str(file_path), remote_path)

