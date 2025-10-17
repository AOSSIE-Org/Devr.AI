from fastapi import APIRouter, Request, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse
from app.database.supabase.client import get_supabase_client
from app.services.auth.verification import find_user_by_session_and_verify, get_verification_session_info
from app.services.github.user.profiling import profile_user_from_github
from typing import Optional
import logging
import asyncio
from typing import TYPE_CHECKING
from app.core.dependencies import get_app_instance
from integrations.discord.views import send_final_handoff_dm

if TYPE_CHECKING:
    from main import DevRAIApplication

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/callback", response_class=HTMLResponse)
async def auth_callback(
    request: Request,
    code: Optional[str] = Query(None),
    session: Optional[str] = Query(None),
    app_instance: "DevRAIApplication" = Depends(get_app_instance),
):
    """
    Handles the OAuth callback from Supabase after a user authorizes on GitHub.
    """
    logger.info(
        f"OAuth callback received with code: {'[PRESENT]' if code else '[MISSING]'}, session: {'[PRESENT]' if session else '[MISSING]'}")

    if not code:
        logger.error("Missing authorization code in callback")
        return _error_response("Missing authorization code. Please try the verification process again.")

    if not session:
        logger.error("Missing session ID in callback")
        return _error_response("Missing session ID. Please try the /verify_github command again.")

    # Check if session is valid and not expired
    session_info = await get_verification_session_info(session)
    if not session_info:
        logger.error(f"Invalid or expired session ID: {session}")
        return _error_response("Your verification session has expired. Please run the /verify_github command again.")

    supabase = get_supabase_client()
    try:
        # Exchange code for session
        logger.info("Exchanging authorization code for session")
        session_response = await supabase.auth.exchange_code_for_session({
            "auth_code": code,
        })

        if not session_response or not session_response.user:
            logger.error("Failed to exchange code for session")
            return _error_response("Authentication failed. Could not retrieve user session.")

        user = session_response.user
        logger.info(f"Successfully got user session for user: {user.id}")

        # Extract GitHub info from user metadata
        github_id = user.user_metadata.get("provider_id")
        github_username = user.user_metadata.get("user_name")
        email = user.email

        if not github_id or not github_username:
            logger.error(f"Missing GitHub details - ID: {github_id}, Username: {github_username}")
            return _error_response("Could not retrieve GitHub details from user session.")

        # Verify user using session ID
        logger.info(f"Verifying user with session ID: {session}")
        verified_user = await find_user_by_session_and_verify(
            session_id=session,
            github_id=str(github_id),
            github_username=github_username,
            email=email
        )

        if not verified_user:
            logger.error("User verification failed - no pending verification found")
            return _error_response("No pending verification found or verification has expired. Please try the /verify_github command again.")

        logger.info(f"Successfully verified user: {verified_user.id}!")

        logger.info(f"Indexing user: {verified_user.id} into Weaviate...")
        try:
            asyncio.create_task(profile_user_from_github(str(verified_user.id), github_username))
            logger.info(f"User profiling started in background for: {verified_user.id}")
        except Exception as e:
            logger.error(f"Error starting user profiling: {verified_user.id}: {str(e)}")

        # Optional: DM the user that they're all set with final hand-off message
        try:
            bot = app_instance.discord_bot if app_instance else None
            if bot and getattr(verified_user, "discord_id", None):
                discord_user = await bot.fetch_user(int(verified_user.discord_id))
                await send_final_handoff_dm(discord_user)
        except Exception as e:
            logger.warning(f"Could not DM verification success: {e}")

        return _success_response(github_username)

    except Exception as e:
        logger.error(f"Unexpected error in OAuth callback: {str(e)}", exc_info=True)

        # Handle specific error cases
        if "already linked" in str(e):
            return _error_response(f"Error: {str(e)}")

        return _error_response("An unexpected error occurred during verification. Please try again.")

@router.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """Get the status of a verification session"""
    session_info = await get_verification_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    return {
        "valid": True,
        "discord_id": session_info["discord_id"],
        "expiry_time": session_info["expiry_time"],
        "time_remaining": session_info["time_remaining"]
    }

def _success_response(github_username: str) -> str:
    """Generate success HTML response"""
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Verification Successful!</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    min-height: 100vh; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0; 
                    padding: 20px;
                    box-sizing: border-box;
                }}
                .container {{ 
                    text-align: center; 
                    padding: 40px; 
                    background: white; 
                    border-radius: 16px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    max-width: 500px;
                    width: 100%;
                }}
                h1 {{ 
                    color: #28a745; 
                    margin-bottom: 20px;
                    font-size: 2rem;
                }}
                .github-info {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid #28a745;
                }}
                code {{ 
                    background: #e9ecef; 
                    padding: 4px 8px; 
                    border-radius: 4px; 
                    font-family: 'Monaco', 'Consolas', monospace;
                    color: #495057;
                    font-weight: bold;
                }}
                .close-btn {{
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: background-color 0.3s;
                }}
                .close-btn:hover {{
                    background: #0056b3;
                }}
                .success-icon {{
                    font-size: 4rem;
                    margin-bottom: 20px;
                }}
                .auto-close {{
                    margin-top: 15px;
                    color: #6c757d;
                    font-size: 0.9rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <h1>Verification Successful!</h1>
                <div class="github-info">
                    <p><strong>Your Discord account has been successfully linked!</strong></p>
                    <p>GitHub User: <code>{github_username}</code></p>
                </div>
                <p>You can now access all features that require GitHub authentication.</p>
                <button class="close-btn" onclick="window.close()">Close Window</button>
                <p class="auto-close">This window will close automatically in 5 seconds.</p>
            </div>
            <script>
                // Auto-close after 5 seconds
                setTimeout(() => {{
                    window.close();
                }}, 5000);
            </script>
        </body>
    </html>
    """

def _error_response(error_message: str) -> str:
    """Generate error HTML response"""
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Verification Failed</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    min-height: 100vh; 
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
                    margin: 0; 
                    padding: 20px;
                    box-sizing: border-box;
                }}
                .container {{ 
                    text-align: center; 
                    padding: 40px; 
                    background: white; 
                    border-radius: 16px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    max-width: 500px;
                    width: 100%;
                }}
                h1 {{ 
                    color: #dc3545; 
                    margin-bottom: 20px;
                    font-size: 2rem;
                }}
                .error-message {{
                    background: #f8d7da;
                    color: #721c24;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid #dc3545;
                }}
                .close-btn {{
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: background-color 0.3s;
                }}
                .close-btn:hover {{
                    background: #c82333;
                }}
                .error-icon {{
                    font-size: 4rem;
                    margin-bottom: 20px;
                }}
                .help-text {{
                    color: #6c757d;
                    font-size: 0.9rem;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1>Verification Failed</h1>
                <div class="error-message">
                    <p>{error_message}</p>
                </div>
                <p>Please return to Discord and try the <code>/verify_github</code> command again.</p>
                <button class="close-btn" onclick="window.close()">Close Window</button>
                <p class="help-text">If you continue to experience issues, please contact support.</p>
            </div>
        </body>
    </html>
    """
