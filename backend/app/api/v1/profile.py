import logging
from fastapi import APIRouter, HTTPException, Depends,status
from app.database.supabase.services import get_user_details, validate_user,update_user_details
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.database.supabase import UserProfileEdit


router = APIRouter()
logger = logging.getLogger(__name__)


security = HTTPBearer()


async def get_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    result = await validate_user(token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"+token,
        )
    return result  


@router.get("/")
async def fetch_details(user=Depends(get_user),):
    """Fetch user profile details."""
    try:
        (id, name) = user
        if not id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        user_details = await get_user_details(id)
        if not user_details:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user": {
            "id": user_details.get("id"),
            "email": user_details.get("email"),
            "display_name": user_details.get("display_name"),
            "avatar_url": user_details.get("avatar_url"),
            "avatar_path": user_details.get("avatar_path"),
            "bio": user_details.get("bio"),
            "discord":user_details.get("discord_username"),
            "github":user_details.get("github_username"),
            "slack":user_details.get("slack_username"),
            "skills": user_details.get("skills") or {"languages": [], "frameworks": []},
        }}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Fetching profile details failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "service": "frontend_services",
                "status": "http exception",
                "error": str(e)
            }
        ) from e


@router.patch("/edit")
async def edit_details(
    profile_data: UserProfileEdit,
    user=Depends(get_user)
):
    """
    Edit user profile details.
    Only updates the fields provided in the request body.
    """
    try:
        (user_id, _) = user
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        update_data = profile_data.model_dump(exclude_unset=True)

        if not update_data:
             raise HTTPException(
                status_code=400, 
                detail="No valid fields provided for update"
            )

        updated_user = await update_user_details(user_id, update_data)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found or update failed")


        return {"user": {
            "id": updated_user.get("id"),
            "email": updated_user.get("email"),
            "display_name": updated_user.get("display_name"),
            "avatar_url": updated_user.get("avatar_url"),
            "avatar_path": updated_user.get("avatar_path"),
            "bio": updated_user.get("bio"),
            "discord": updated_user.get("discord_username"),
            "github": updated_user.get("github_username"),
            "slack": updated_user.get("slack_username"),
            "skills": updated_user.get("skills") or [],
        }}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Updating profile details failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "service": "frontend_services",
                "status": "http exception",
                "error": str(e)
            }
        ) from e