import os
import sys
import logging

from fastapi import Depends, UploadFile, File, APIRouter
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Setup project path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.critical("Failed to set up project base path: %s", e)
    sys.exit(1)

# Local imports
from src.helpers import get_settings, Settings
from src.infra import setup_logging
from src.auth import get_current_user

# Load settings and logger
app_settings: Settings = get_settings()
logger = setup_logging(name="ROUTE-PROFILE")


import os
import sys
import logging
from pathlib import Path

from fastapi import Depends, UploadFile, File, APIRouter, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_404_NOT_FOUND

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Setup project path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
    WEB_DIR = Path(MAIN_DIR) / "web"  # Add this line
except (ImportError, OSError) as e:
    logging.critical("Failed to set up project base path: %s", e)
    sys.exit(1)

# Local imports
from src.helpers import get_settings, Settings
from src.infra import setup_logging
from src.auth import get_current_user

# Load settings and logger
app_settings: Settings = get_settings()
logger = setup_logging(name="ROUTE-PROFILE")

# FastAPI route group
profile_route = APIRouter(
    prefix="/api/v1",
    tags=["ROUTE-PROFILE"],
    responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@profile_route.post("/upload-profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        return JSONResponse(status_code=400, content={"error": "Invalid image type"})

    ext = file.filename.split(".")[-1]
    filename = f"{user['user_name']}.{ext}"

    image_dir = os.path.join(MAIN_DIR, "media", "profiles")
    os.makedirs(image_dir, exist_ok=True)

    save_path = os.path.join(image_dir, filename)
    with open(save_path, "wb") as buffer:
        buffer.write(await file.read())

    user["image_filename"] = filename  # Optional: persist this in DB

    # ✅ Return public-facing URL path
    return {"image_url": f"/media/profiles/{filename}"}


@profile_route.get("/profile-image-url")
async def get_profile_image_url(user: dict = Depends(get_current_user)):
    """
    Returns the profile image URL or initials for the user.
    """
    image_filename = user.get("image_filename")
    if image_filename:
        image_url = f"/media/profiles/{image_filename}"
        return {"image_url": image_url}
    else:
        full_name = user.get("full_name", "??")
        initials = ''.join([part[0].upper() for part in full_name.split()[:2]])
        return {"image_url": None, "initials": initials}


@profile_route.delete("/remove-profile-image")
async def delete_profile_image(user: dict = Depends(get_current_user)):
    image_filename = user.get("image_filename")
    if image_filename:
        image_path = os.path.join(MAIN_DIR, "media", "profiles", image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
        # Update user record to remove image_filename
        user["image_filename"] = None
    return {"message": "Image deleted successfully"}
