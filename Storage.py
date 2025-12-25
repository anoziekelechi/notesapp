from pathlib import Path
import uuid

def generate_unique_key(prefix: str, original_filename: str) -> str:
    path = Path(original_filename)
    
    stem = path.stem
    extension = path.suffix.lower() or ".jpg"   # fallback if no extension
    
    # Option A: simple uuid
    # unique_name = f"{uuid.uuid4()}{extension}"
    
    # Option B: keep original name + short unique suffix (most readable)
    short_uuid = uuid.uuid4().hex[:8]           # first 8 chars = enough uniqueness
    unique_name = f"{stem}-{short_uuid}{extension}"
    
    return f"{prefix}/{unique_name}"



def delete_from_s3(key: str | None) -> None:
    """Best-effort delete from S3"""
    if not key:
        return
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
    except Exception:
        pass  # silent fail - log in production


def get_public_url(key: str | None) -> str | None:
    """
    Generate permanent public URL.
    Uses CDN domain if configured, otherwise direct S3 URL.
    """
    if not key:
        return None

    if CDN_DOMAIN:
        return f"https://{CDN_DOMAIN}/{key}"
    
    # Fallback: direct S3 public URL
    region = "us-east-1"  # ← take from config if possible
    return f"https://{BUCKET_NAME}.s3.{region}.amazonaws.com/{key}"





# services/storage.py final adjustment 
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from botocore.exceptions import ClientError

from ..config.settings import settings   # your Settings class
from .s3_utils import s3_client, BUCKET_NAME, generate_unique_key
from ..services.validation import validate_image_file_securely  # assuming you have this


async def handle_file_update(
    file: Optional[UploadFile],
    current_key: Optional[str],
    prefix: str,                     # e.g. "home/logo", "home/hero"
    max_size: int,
    validator=validate_image_file_securely,  # default validator
) -> Optional[str]:
    """
    Handle file upload/update flow:
    - Validates the file
    - Uploads to S3 with environment-specific prefix (dev/prod)
    - Deletes old file if exists
    - Returns the final stored key (with prefix) or keeps current if no new file

    Returns:
        str | None: final S3 key to store in database
    """
    if not file:
        # No new file uploaded → keep existing key
        return current_key

    # 1. Early size validation (cheap check)
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (maximum allowed: {max_size // (1024 * 1024)}MB)"
        )

    # 2. Secure content-type validation using libmagic
    await validator(file)

    # 3. Generate base key (without environment prefix yet)
    base_key = generate_unique_key(prefix, file.filename)

    # 4. Add environment-specific prefix (development/ or production/)
    env_prefix = settings.image_prefix   # 'development/' or 'production/'
    final_key = f"{env_prefix}{base_key}"

    # 5. Upload to S3 with public-read
    try:
        await upload_to_s3(
            file=file.file,
            key=final_key,
            content_type=file.content_type
        )
    except HTTPException as exc:
        # Re-raise the same exception from upload_to_s3
        raise exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {exc.__class__.__name__}"
        ) from exc

    # 6. Best-effort cleanup of previous file
    if current_key:
        try:
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=current_key)
        except Exception:
            pass  # silent fail - consider logging in production

    # 7. Return the final key (with env prefix) to be stored in DB
    return final_key


# app/schemas/home.py
from typing import Optional
from sqlmodel import SQLModel


class HomeResponse(SQLModel):
    sitename: str
    logo_url: Optional[str] = None
    image_url: Optional[str] = None

# app/routers/home/logics.py
from typing import Optional
from fastapi import HTTPException, status, UploadFile
from sqlmodel import Session, select

from ...models import Home
from ...schemas.home import HomeResponse
from ...services.storage import handle_file_update, get_public_url
from ...services.validation import validate_image_file_securely

LOGO_MAX_SIZE = 5 * 1024 * 1024    # 5 MiB
HERO_MAX_SIZE = 8 * 1024 * 1024    # 8 MiB


async def setup_home_logic(
    session: Session,
    sitename: str,
    aboutus: Optional[str] = None,
    introduction: Optional[str] = None,
    logo: Optional[UploadFile] = None,
    hero_image: Optional[UploadFile] = None,
) -> HomeResponse:
    """Business logic: create/update home config + generate public URLs"""
    stmt = select(Home).where(Home.config_type == "MAIN")
    current = session.exec(stmt).first()

    new_logo_key = await handle_file_update(
        file=logo,
        current_key=current.logo_key if current else None,
        prefix="home/logo",
        max_size=LOGO_MAX_SIZE,
        validator=validate_image_file_securely
    )

    new_hero_key = await handle_file_update(
        file=hero_image,
        current_key=current.image_key if current else None,
        prefix="home/hero",
        max_size=HERO_MAX_SIZE,
        validator=validate_image_file_securely
    )

    try:
        if current is None:
            record = Home(
                config_type="MAIN",
                sitename=sitename,
                aboutus=aboutus,
                introduction=introduction,
                logo_key=new_logo_key,
                image_key=new_hero_key,
            )
            session.add(record)
        else:
            current.sitename = sitename
            if aboutus is not None:
                current.aboutus = aboutus
            if introduction is not None:
                current.introduction = introduction

            if logo is not None:
                current.logo_key = new_logo_key
            if hero_image is not None:
                current.image_key = new_hero_key

            record = current

        session.commit()
        session.refresh(record)

        return HomeResponse(
            sitename=record.sitename,
            logo_url=get_public_url(record.logo_key),
            image_url=get_public_url(record.image_key),
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}") from e


def get_home_settings_logic(session: Session) -> HomeResponse:
    """Fetch MAIN home config with permanent public URLs"""
    stmt = select(Home).where(Home.config_type == "MAIN")
    home = session.exec(stmt).first()

    if not home:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home settings not initialized"
        )

    return HomeResponse(
        sitename=home.sitename,
        logo_url=get_public_url(home.logo_key),
        image_url=get_public_url(home.image_key),
    )
# app/routers/home/routes.py
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    status,
)
from typing import Annotated
from sqlmodel import Session

from ...dependencies import get_session
from ...schemas.home import HomeResponse
from .logics import setup_home_logic, get_home_settings_logic

router = APIRouter(prefix="/home", tags=["Home Configuration"])


@router.post("/setup", status_code=status.HTTP_201_CREATED, response_model=HomeResponse)
async def setup_home(
    sitename: Annotated[str, Form(min_length=1, max_length=120)],
    aboutus: Annotated[str | None, Form(max_length=2000)] = None,
    introduction: Annotated[str | None, Form(max_length=1200)] = None,
    
    logo: Annotated[UploadFile | None, File()] = None,
    hero_image: Annotated[UploadFile | None, File()] = None,
    
    session: Session = Depends(get_session),
) -> HomeResponse:
    """
    Create or update the MAIN home page configuration (public URLs)
    """
    return await setup_home_logic(
        session=session,
        sitename=sitename,
        aboutus=aboutus,
        introduction=introduction,
        logo=logo,
        hero_image=hero_image,
    )


@router.get("", response_model=HomeResponse)
def get_home_settings(session: Session = Depends(get_session)) -> HomeResponse:
    """
    Get current public home page configuration with permanent public URLs
    """
    return get_home_settings_logic(session=session)


# app/services/storage.py
# services/storage.py
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from ..config.settings import settings   # or use Depends(get_settings)

async def upload_to_s3(
    file,
    key: str,
    content_type: str | None = None
) -> str:
    """
    Returns the final S3 key that was used (with prefix)
    """
    # Add environment-specific prefix
    prefixed_key = f"{settings.image_prefix}{key}"

    try:
        s3_client.upload_fileobj(
            file,
            BUCKET_NAME,
            prefixed_key,
            ExtraArgs={
                "ContentType": content_type or "image/jpeg",
                "ACL": "public-read",
                "CacheControl": "max-age=31536000, public"  # 1 year
            }
        )
        return prefixed_key  # ← return it so you can save correct key in DB

    except ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"S3 upload failed: {e.__class__.__name__}"
        ) from e
  
