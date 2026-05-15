from fastapi import APIRouter, Cookie, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.user.schemas import UserRead
from src.zip_url.service import ZipURLService

router = APIRouter(prefix="/zip-url", tags=["zip-url"])

clear_router = APIRouter(prefix="", tags=["zip-url"])



@router.post("/create-zip-url")
async def zip_url(
    url: str,
    session_token: str | None = Cookie(default=None),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    service = ZipURLService(db)
    zipped_url = await service.create_zip_url(url, current_user)
    return {"message": "Created successfully.", "originalUrl": url, "zipped_url": zipped_url}



@clear_router.get("/{url_token}")
async def go_to_original_url(
    url_token: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    service = ZipURLService(db)
    original_url = await service.get_original_url_by_url_token(url_token)
    if not original_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    return RedirectResponse(
        url=original_url
    )