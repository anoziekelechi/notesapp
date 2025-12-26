
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


@router.post(
    "/setup",
    status_code=status.HTTP_201_CREATED,
    response_model=HomeResponse,
    summary="Create or update home page configuration",
    description="Updates the singleton MAIN home configuration. "
                "Partial updates supported for text fields. "
                "New images replace old ones with cleanup."
)
async def setup_home(
    sitename: Annotated[str, Form(min_length=1, max_length=120)],
    aboutus: Annotated[str | None, Form(max_length=2000)] = None,
    introduction: Annotated[str | None, Form(max_length=1200)] = None,
    
    logo: Annotated[UploadFile | None, File()] = None,
    hero_image: Annotated[UploadFile | None, File()] = None,
    
    session: Session = Depends(get_session),
) -> HomeResponse:
    """
    Endpoint for admin to configure home page settings
    """
    return await setup_home_logic(
        session=session,
        sitename=sitename,
        aboutus=aboutus,
        introduction=introduction,
        logo=logo,
        hero_image=hero_image,
    )


@router.get(
    "",
    response_model=HomeResponse,
    summary="Get current home page configuration",
    description="Returns public home settings including permanent image URLs"
)
def get_home_settings(
    session: Session = Depends(get_session)
) -> HomeResponse:
    """
    Public endpoint to fetch home page configuration
    """
    return get_home_settings_logic(session=session)


# app/routers/home/logics.py
from typing import Optional
from fastapi import HTTPException, status, UploadFile
from sqlmodel import Session, select

from ...models import Home
from ...schemas.home import HomeResponse
from ...services.storage import handle_file_update, get_public_url
from ...services.validation import validate_image_file_securely

LOGO_MAX_SIZE = 5 * 1024 * 1024   # 5 MiB
HERO_MAX_SIZE = 8 * 1024 * 1024   # 8 MiB


async def setup_home_logic(
    session: Session,
    sitename: str,
    aboutus: Optional[str] = None,
    introduction: Optional[str] = None,
    logo: Optional[UploadFile] = None,
    hero_image: Optional[UploadFile] = None,
) -> HomeResponse:
    """
    Create or update MAIN home configuration
    Returns response with public image URLs
    """
    stmt = select(Home).where(Home.config_type == "MAIN")
    current = session.exec(stmt).first()

    # Handle file updates (with env-specific prefix)
    new_logo_key = await handle_file_update(
        file=logo,
        current_key=current.logo_key if current else None,
        prefix="home/logo",
        max_size=LOGO_MAX_SIZE,
        validator=validate_image_file_securely,
    )

    new_hero_key = await handle_file_update(
        file=hero_image,
        current_key=current.image_key if current else None,
        prefix="home/hero",
        max_size=HERO_MAX_SIZE,
        validator=validate_image_file_securely,
    )

    try:
        if current is None:
            # First time creation
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
            # Partial update
            current.sitename = sitename

            if aboutus is not None:
                current.aboutus = aboutus
            if introduction is not None:
                current.introduction = introduction

            # Only update file keys if new file was provided
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save home configuration: {str(e)}"
        ) from e


def get_home_settings_logic(session: Session) -> HomeResponse:
    """
    Fetch the MAIN home configuration with public URLs
    """
    stmt = select(Home).where(Home.config_type == "MAIN")
    home = session.exec(stmt).first()

    if not home:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home page settings not yet configured"
        )

    return HomeResponse(
        sitename=home.sitename,
        logo_url=get_public_url(home.logo_key),
        image_url=get_public_url(home.image_key),
    )
