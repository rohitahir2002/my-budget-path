from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import BudgetPlanData, BudgetPlanOut
from app.database import get_budget_collection
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/budget", tags=["Budget Plan"])


@router.get("/plan", response_model=BudgetPlanOut)
async def get_budget_plan(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the current user's saved budget plan.
    Data isolation: strictly filtered by current_user['id'].
    """
    budget_col = get_budget_collection()
    if budget_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    user_id = current_user["id"]
    plan = await budget_col.find_one({"user_id": user_id})

    if not plan:
        # Default plan if user doesn't have one saved yet
        now_iso = datetime.now(timezone.utc).isoformat()
        return BudgetPlanOut(
            user_id=user_id,
            monthly_income=45000.0,
            savings_goal=100000.0,
            months_target=12,
            current_savings=10000.0,
            annual_return_rate=6.0,
            needs=[
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
            investments=[
                {"n": "Fixed deposit (FD)", "a": 2000.0, "r": 7.0},
                {"n": "Recurring deposit (RD)", "a": 0.0, "r": 6.5},
                {"n": "Mutual fund SIP", "a": 2000.0, "r": 11.0},
                {"n": "Stocks", "a": 1000.0, "r": 12.0},
                {"n": "PPF", "a": 500.0, "r": 7.1},
                {"n": "Gold", "a": 0.0, "r": 8.0}
            ],
            updated_at=now_iso
        )

    return BudgetPlanOut(
        user_id=user_id,
        monthly_income=plan.get("monthly_income", 45000.0),
        savings_goal=plan.get("savings_goal", 100000.0),
        months_target=plan.get("months_target", 12),
        current_savings=plan.get("current_savings", 10000.0),
        annual_return_rate=plan.get("annual_return_rate", 6.0),
        needs=plan.get("needs", []),
        investments=plan.get("investments", []),
        updated_at=plan.get("updated_at", datetime.now(timezone.utc).isoformat())
    )


@router.post("/plan", response_model=BudgetPlanOut)
async def save_budget_plan(
    payload: BudgetPlanData,
    current_user: dict = Depends(get_current_user)
):
    """
    Save or update the current user's budget plan in MongoDB.
    Strictly isolated: updates only the document matching current_user['id'].
    """
    budget_col = get_budget_collection()
    if budget_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    user_id = current_user["id"]
    now_iso = datetime.now(timezone.utc).isoformat()

    doc = {
        "user_id": user_id,
        "monthly_income": payload.monthly_income,
        "savings_goal": payload.savings_goal,
        "months_target": payload.months_target,
        "current_savings": payload.current_savings,
        "annual_return_rate": payload.annual_return_rate,
        "needs": [item.dict() for item in payload.needs],
        "investments": [item.dict() for item in payload.investments],
        "updated_at": now_iso
    }

    await budget_col.update_one(
        {"user_id": user_id},
        {"$set": doc},
        upsert=True
    )

    return BudgetPlanOut(
        user_id=user_id,
        monthly_income=payload.monthly_income,
        savings_goal=payload.savings_goal,
        months_target=payload.months_target,
        current_savings=payload.current_savings,
        annual_return_rate=payload.annual_return_rate,
        needs=payload.needs,
        investments=payload.investments,
        updated_at=now_iso
    )
