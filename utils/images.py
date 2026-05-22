"""Image handling utilities."""
import os
import time
import requests
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app
from typing import Optional
from urllib.parse import urlparse


def ensure_directories():
    """Ensure upload and avatar directories exist."""
    upload_dir = current_app.config.get('UPLOAD_FOLDER')
    avatar_dir = current_app.config.get('AVATAR_FOLDER')
    
    if upload_dir:
        os.makedirs(upload_dir, exist_ok=True)
    if avatar_dir:
        os.makedirs(avatar_dir, exist_ok=True)


def download_cover_if_external(url: str) -> str:
    """
    Download external image URL to local storage.
    
    Args:
        url: Image URL (can be external or local)
        
    Returns:
        Local path if downloaded, original URL otherwise
    """
    if not url:
        return url
    
    url = url.strip()
    
    # If already local path, return as is
    if not (url.startswith('http://') or url.startswith('https://')):
        return url
    
    ensure_directories()
    upload_dir = current_app.config.get('UPLOAD_FOLDER')
    allowed_ext = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    
    try:
        # Download image
        response = requests.get(url, timeout=8, stream=True)
        if response.status_code != 200 or not response.content:
            return url
        
        # Determine filename
        parsed = urlparse(url)
        name = os.path.basename(parsed.path) or f"cover_{int(time.time())}.jpg"
        safe_name = secure_filename(name)
        
        # Ensure valid extension
        ext = safe_name.rsplit('.', 1)[-1].lower() if '.' in safe_name else 'jpg'
        if ext not in allowed_ext:
            ext = 'jpg'
            safe_name = f"{safe_name.rsplit('.', 1)[0]}.{ext}" if '.' in safe_name else f"{safe_name}.{ext}"
        
        # Generate unique filename to avoid overwrites
        dest_path = Path(upload_dir) / safe_name
        base, dot, ex = safe_name.rpartition('.')
        counter = 1
        while dest_path.exists():
            safe_name = f"{base}_{counter}.{ex}"
            dest_path = Path(upload_dir) / safe_name
            counter += 1
        
        # Save file
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Return relative path for web
        return f'/static/uploads/{safe_name}'
        
    except Exception as e:
        current_app.logger.error(f"Error downloading cover image: {e}")
        return url


def find_avatar_filename(user_id: int) -> Optional[str]:
    """Find avatar filename for a user."""
    import glob
    avatar_dir = current_app.config.get('AVATAR_FOLDER')
    pattern = os.path.join(avatar_dir, f"{user_id}.*")
    matches = glob.glob(pattern)
    if matches:
        return os.path.basename(matches[0])
    return None


def remove_existing_avatars(user_id: int):
    """Remove all existing avatars for a user."""
    import glob
    avatar_dir = current_app.config.get('AVATAR_FOLDER')
    pattern = os.path.join(avatar_dir, f"{user_id}.*")
    for path in glob.glob(pattern):
        try:
            os.remove(path)
        except Exception:
            pass

