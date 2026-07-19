from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .config import get_settings
from .db import get_session
from .models import OAuthAccount, User
from .orchestrator import Orchestrator
from .repositories import GoalRepository, TaskRepository, UserRepository
from .schemas import (
    AIRequest,
    AIResponse,
    DailyBrief,
    GoalCreate,
    GoalRead,
    LoginRequest,
    RegisterRequest,
    TaskCreate,
    TaskRead,
    TaskUpdate,
    TokenResponse,
    UserRead,
)
from .security import create_access_token, decode_access_token, encrypt_credential
from .services import AuthService, GoalService, TaskService

orchestrator = Orchestrator(get_settings())

app = FastAPI(
    title="LifeOS API",
    version="0.2.0",
    description="Personal operating system API. All resources are user scoped.",
)
app.add_middleware(
    SessionMiddleware,
    secret_key=get_settings().jwt_secret,
    https_only=False,
    same_site="lax",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
oauth = OAuth()
if get_settings().oauth_google_client_id and get_settings().oauth_google_client_secret:
    oauth.register(
        name="google",
        client_id=get_settings().oauth_google_client_id,
        client_secret=get_settings().oauth_google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
bearer = HTTPBearer()


def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_session),
) -> User:
    user = session.get(User, decode_access_token(credentials.credentials))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )
    return user


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/auth/register", response_model=UserRead, status_code=201, tags=["auth"])
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    return AuthService(session).register(data)


@app.post("/v1/auth/token", response_model=TokenResponse, tags=["auth"])
def token(data: LoginRequest, session: Session = Depends(get_session)):
    user = AuthService(session).authenticate(str(data.email), data.password)
    return TokenResponse(access_token=create_access_token(user.id))


@app.get("/v1/auth/oauth/google/login", tags=["auth"])
async def google_login(request: Request):
    if not get_settings().oauth_google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")
    return await oauth.google.authorize_redirect(
        request,
        f"{get_settings().oauth_redirect_base_url}/v1/auth/oauth/google/callback",
    )


@app.get("/v1/auth/oauth/google/callback", response_model=TokenResponse, tags=["auth"])
async def google_callback(request: Request, session: Session = Depends(get_session)):
    if not get_settings().oauth_google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")
    token_data = await oauth.google.authorize_access_token(request)
    claims = token_data.get("userinfo") or await oauth.google.parse_id_token(
        request, token_data
    )
    email = claims.get("email")
    if not email or not claims.get("email_verified"):
        raise HTTPException(
            status_code=401, detail="Google did not return a verified email"
        )
    users = UserRepository(session)
    user = users.by_email(email)
    if not user:
        from .models import Profile, User

        user = User(email=email.lower(), password_hash=None)
        session.add(user)
        session.flush()
        session.add(Profile(user_id=user.id, display_name=claims.get("name") or email))
        session.commit()
        session.refresh(user)
    provider_id = str(claims.get("sub"))
    account = (
        session.query(OAuthAccount)
        .filter_by(provider="google", provider_account_id=provider_id)
        .one_or_none()
    )
    if account is None:
        account = OAuthAccount(
            user_id=user.id, provider="google", provider_account_id=provider_id
        )
        session.add(account)
    account.access_token_encrypted = encrypt_credential(token_data.get("access_token"))
    account.refresh_token_encrypted = encrypt_credential(
        token_data.get("refresh_token")
    )
    session.commit()
    return TokenResponse(access_token=create_access_token(user.id))


@app.get("/v1/tasks", response_model=list[TaskRead], tags=["tasks"])
def list_tasks(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    return TaskRepository(session).list_for_user(user.id)


@app.post("/v1/tasks", response_model=TaskRead, status_code=201, tags=["tasks"])
def create_task(
    data: TaskCreate,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    return TaskService(session).create(user.id, data)


@app.patch("/v1/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
def update_task(
    task_id: str,
    data: TaskUpdate,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    return TaskService(session).update(user.id, task_id, data)


@app.get("/v1/goals", response_model=list[GoalRead], tags=["goals"])
def list_goals(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    return GoalRepository(session).list_for_user(user.id)


@app.post("/v1/goals", response_model=GoalRead, status_code=201, tags=["goals"])
def create_goal(
    data: GoalCreate,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    return GoalService(session).create(user.id, data)


@app.get("/v1/daily-brief", response_model=DailyBrief, tags=["daily"])
def daily_brief(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    tasks = TaskRepository(session).list_for_user(user.id)
    open_tasks = [task for task in tasks if task.status != "completed"]
    return DailyBrief(
        open_tasks=len(open_tasks),
        high_priority_tasks=sorted(open_tasks, key=lambda task: task.priority)[:3],
        focus_recommendation="Protect one 25-minute focus block before processing new requests.",
    )


@app.post("/v1/ai/respond", response_model=AIResponse, tags=["ai"])
async def ai_respond(data: AIRequest, user: User = Depends(current_user)):
    """Route an explicit request to one specialist agent; no memory or tools are used."""
    return await orchestrator.respond(data)
