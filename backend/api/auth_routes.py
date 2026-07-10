from fastapi import APIRouter, HTTPException, Depends, Header
from models.schemas import RegisterRequest, LoginRequest, TokenResponse
from auth.jwt_utils import hash_password, verify_password, create_access_token, decode_access_token
from database import mongo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest):
    if mongo.get_user_by_email(req.email):
        raise HTTPException(status_code=400, detail="Email already registered.")
    mongo.create_user(req.email, hash_password(req.password), req.name)
    token = create_access_token(req.email)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = mongo.get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = create_access_token(req.email)
    return TokenResponse(access_token=token)


def get_current_user(authorization: str = Header(default="")) -> str:
    """Dependency to protect routes. Expects 'Bearer <token>'."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header.")
    token = authorization.split(" ", 1)[1]
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return email
