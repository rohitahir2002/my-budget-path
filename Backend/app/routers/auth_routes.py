from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import UserRegister, UserLogin, UserOut, Token
from app.auth import hash_password, verify_password, create_access_token
from app.database import get_users_collection, get_budget_collection
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    users_col = get_users_collection()
    if users_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available. Please verify MongoDB connection string in .env"
        )

    email_clean = payload.email.strip().lower()
    username_clean = payload.username.strip().lower()

    if len(payload.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )

    # Check if user already exists
    existing_user = await users_col.find_one({
        "$or": [{"email": email_clean}, {"username": username_clean}]
    })
    if existing_user:
        if existing_user.get("email") == email_clean:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This username is already taken. Please choose another."
            )

    # Validate role - default to user, allow admin if specified (or if username/email contains admin)
    role = payload.role.strip().lower()
    if role not in ["user", "admin"]:
        role = "user"

    now_iso = datetime.now(timezone.utc).isoformat()
    new_user_doc = {
        "email": email_clean,
        "username": username_clean,
        "full_name": payload.full_name or payload.username,
        "password_hash": hash_password(payload.password),
        "role": role,
        "is_active": True,
        "created_at": now_iso
    }

    result = await users_col.insert_one(new_user_doc)
    user_id = str(result.inserted_id)

    # Create initial budget plan for new user
    budget_col = get_budget_collection()
    if budget_col is not None:
        default_plan = {
            "user_id": user_id,
            "monthly_income": 45000.0,
            "savings_goal": 100000.0,
            "months_target": 12,
            "current_savings": 10000.0,
            "annual_return_rate": 6.0,
            "needs": [
                {"n": "Rent", "a": 12000.0},
                {"n": "EMI / loan", "a": 8000.0},
                {"n": "Food & groceries", "a": 6000.0},
                {"n": "Utilities (electricity, water, gas)", "a": 2000.0},
                {"n": "Transport / fuel", "a": 2500.0},
                {"n": "Health & medicine", "a": 1000.0},
                {"n": "Insurance premium", "a": 1500.0},
                {"n": "School / tuition fees", "a": 2000.0},
                {"n": "Mobile & internet", "a": 800.0}
            ],
            "investments": [
                {"n": "Fixed deposit (FD)", "a": 2000.0, "r": 7.0},
                {"n": "Recurring deposit (RD)", "a": 0.0, "r": 6.5},
                {"n": "Mutual fund SIP", "a": 2000.0, "r": 11.0},
                {"n": "Stocks", "a": 1000.0, "r": 12.0},
                {"n": "PPF", "a": 500.0, "r": 7.1},
                {"n": "Gold", "a": 0.0, "r": 8.0}
            ],
            "updated_at": now_iso
        }
        await budget_col.insert_one(default_plan)

    # Issue JWT token
    token_data = {"sub": user_id, "role": role, "email": email_clean}
    access_token = create_access_token(token_data)

    user_out = UserOut(
        id=user_id,
        email=email_clean,
        username=username_clean,
        full_name=new_user_doc["full_name"],
        role=role,
        created_at=now_iso,
        is_active=True
    )

    return Token(access_token=access_token, token_type="bearer", user=user_out)


@router.post("/login", response_model=Token)
async def login(payload: UserLogin):
    users_col = get_users_collection()
    if users_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    identifier = payload.email_or_username.strip().lower()
    user = await users_col.find_one({
        "$or": [{"email": identifier}, {"username": identifier}]
    })

    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password."
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact an administrator."
        )

    user_id = str(user["_id"])
    role = user.get("role", "user")

    token_data = {"sub": user_id, "role": role, "email": user["email"]}
    access_token = create_access_token(token_data)

    user_out = UserOut(
        id=user_id,
        email=user["email"],
        username=user["username"],
        full_name=user.get("full_name", user["username"]),
        role=role,
        created_at=user.get("created_at", ""),
        is_active=user.get("is_active", True)
    )

    return Token(access_token=access_token, token_type="bearer", user=user_out)


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    return UserOut(
        id=current_user["id"],
        email=current_user["email"],
        username=current_user["username"],
        full_name=current_user.get("full_name", current_user["username"]),
        role=current_user.get("role", "user"),
        created_at=current_user.get("created_at", ""),
        is_active=current_user.get("is_active", True)
    )
