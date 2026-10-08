from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import UserOut, AdminUserUpdate, SystemStats
from app.database import (
    get_users_collection,
    get_transactions_collection,
    get_budget_collection,
    get_db
)
from app.dependencies import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Portal (RBAC)"])


@router.get("/users", response_model=List[UserOut])
async def list_all_users(admin: dict = Depends(require_admin)):
    """
    [Admin Only] List all registered users in the platform.
    Protected by RBAC (Role-Based Access Control).
    """
    users_col = get_users_collection()
    if users_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    cursor = users_col.find().sort("created_at", -1)
    results = []
    async for u in cursor:
        results.append(UserOut(
            id=str(u["_id"]),
            email=u.get("email", ""),
            username=u.get("username", ""),
            full_name=u.get("full_name", ""),
            role=u.get("role", "user"),
            created_at=u.get("created_at", ""),
            is_active=u.get("is_active", True)
        ))
    return results


@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user_status_or_role(
    user_id: str,
    payload: AdminUserUpdate,
    admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Change user role (e.g., promote to admin or demote to user)
    or deactivate/activate an account.
    """
    users_col = get_users_collection()
    if users_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format."
        )

    update_fields = {}
    if payload.role is not None:
        if payload.role not in ["user", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be either 'user' or 'admin'."
            )
        update_fields["role"] = payload.role
    if payload.is_active is not None:
        update_fields["is_active"] = payload.is_active

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update provided."
        )

    result = await users_col.find_one_and_update(
        {"_id": obj_id},
        {"$set": update_fields},
        return_document=True
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return UserOut(
        id=str(result["_id"]),
        email=result.get("email", ""),
        username=result.get("username", ""),
        full_name=result.get("full_name", ""),
        role=result.get("role", "user"),
        created_at=result.get("created_at", ""),
        is_active=result.get("is_active", True)
    )


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(admin: dict = Depends(require_admin)):
    """
    [Admin Only] Get aggregate statistics and platform analytics.
    """
    users_col = get_users_collection()
    tx_col = get_transactions_collection()
    budget_col = get_budget_collection()
    db = get_db()

    if None in (users_col, tx_col, budget_col, db):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    total_users = await users_col.count_documents({})
    active_users = await users_col.count_documents({"is_active": True})
    admin_users = await users_col.count_documents({"role": "admin"})
    total_tx = await tx_col.count_documents({})
    total_plans = await budget_col.count_documents({})

    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        admin_users=admin_users,
        total_transactions=total_tx,
        total_budget_plans=total_plans,
        mongodb_status="Connected & Healthy"
    )
