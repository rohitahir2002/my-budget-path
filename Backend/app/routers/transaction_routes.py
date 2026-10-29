from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models import TransactionCreate, TransactionOut
from app.database import get_transactions_collection
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionOut])
async def list_transactions(
    type: Optional[str] = Query(None, description="Filter by 'expense' or 'income'"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """
    List transactions for the authenticated user only.
    Data isolation: strictly filtered by user_id = current_user['id'].
    """
    tx_col = get_transactions_collection()
    if tx_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    filter_query = {"user_id": current_user["id"]}
    if type:
        filter_query["type"] = type.lower()
    if category:
        filter_query["category"] = category

    cursor = tx_col.find(filter_query).sort("date", -1).limit(limit)
    records = []
    async for doc in cursor:
        records.append(TransactionOut(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            date=doc["date"],
            title=doc.get("title", ""),
            category=doc["category"],
            amount=doc["amount"],
            type=doc["type"],
            payment_method=doc.get("payment_method", "UPI"),
            notes=doc.get("notes", ""),
            created_at=doc.get("created_at", "")
        ))
    return records


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new transaction tied to the authenticated user.
    """
    tx_col = get_transactions_collection()
    if tx_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    doc = {
        "user_id": current_user["id"],
        "date": payload.date,
        "title": payload.title,
        "category": payload.category,
        "amount": payload.amount,
        "type": payload.type.lower(),
        "payment_method": payload.payment_method,
        "notes": payload.notes or "",
        "created_at": now_iso
    }

    result = await tx_col.insert_one(doc)
    return TransactionOut(
        id=str(result.inserted_id),
        user_id=current_user["id"],
        date=doc["date"],
        title=doc["title"],
        category=doc["category"],
        amount=doc["amount"],
        type=doc["type"],
        payment_method=doc["payment_method"],
        notes=doc["notes"],
        created_at=now_iso
    )


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    tx_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a transaction. Must belong to the current user.
    """
    tx_col = get_transactions_collection()
    if tx_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    try:
        obj_id = ObjectId(tx_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID format."
        )

    result = await tx_col.delete_one({"_id": obj_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found or unauthorized to delete."
        )
    return None


@router.get("/summary")
async def get_transaction_summary(current_user: dict = Depends(get_current_user)):
    """
    Aggregate transaction statistics for current user: total expenses, total income, net balance.
    """
    tx_col = get_transactions_collection()
    if tx_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    pipeline = [
        {"$match": {"user_id": current_user["id"]}},
        {
            "$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }
        }
    ]
    cursor = tx_col.aggregate(pipeline)
    totals = {"expense": 0.0, "income": 0.0, "expense_count": 0, "income_count": 0}
    async for row in cursor:
        t = row["_id"]
        if t in totals:
            totals[t] = row["total"]
            totals[f"{t}_count"] = row["count"]

    net_balance = totals["income"] - totals["expense"]
    return {
        "total_income": totals["income"],
        "total_expense": totals["expense"],
        "net_balance": net_balance,
        "income_count": totals["income_count"],
        "expense_count": totals["expense_count"]
    }


@router.get("/monthly-stats")
async def get_monthly_transaction_stats(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format (e.g., 2024-10)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Detailed monthly transaction statistics and time-series aggregations
    for interactive charts and category velocity tracking.
    """
    tx_col = get_transactions_collection()
    if tx_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    user_id = current_user["id"]
    cursor = tx_col.find({"user_id": user_id}).sort("date", 1)
    all_tx = await cursor.to_list(length=1000)

    # 1. Determine all unique available months (YYYY-MM)
    all_months = sorted(list(set(t["date"][:7] for t in all_tx if len(t.get("date", "")) >= 7)), reverse=True)
    current_month_str = datetime.now(timezone.utc).strftime("%Y-%m")
    if not all_months:
        all_months = [current_month_str]

    selected_month = month if (month and month in all_months) else all_months[0]

    # 2. Filter for selected month
    month_tx = [t for t in all_tx if t.get("date", "").startswith(selected_month)]

    total_income = sum(t["amount"] for t in month_tx if t.get("type") == "income")
    total_expense = sum(t["amount"] for t in month_tx if t.get("type") == "expense")
    net_savings = total_income - total_expense
    savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

    # 3. Category breakdown for selected month
    cat_map = {}
    for t in month_tx:
        if t.get("type") == "expense":
            c = t.get("category", "Other")
            cat_map[c] = cat_map.get(c, 0.0) + t.get("amount", 0.0)

    category_breakdown = [
        {
            "category": k,
            "amount": v,
            "percentage": round((v / total_expense * 100), 1) if total_expense > 0 else 0.0
        }
        for k, v in sorted(cat_map.items(), key=lambda x: x[1], reverse=True)
    ]

    # 4. Payment method breakdown for selected month
    pay_map = {}
    for t in month_tx:
        p = t.get("payment_method", "Other")
        pay_map[p] = pay_map.get(p, 0.0) + t.get("amount", 0.0)

    tot_pay = sum(pay_map.values())
    payment_methods = [
        {
            "method": k,
            "amount": v,
            "percentage": round((v / tot_pay * 100), 1) if tot_pay > 0 else 0.0
        }
        for k, v in sorted(pay_map.items(), key=lambda x: x[1], reverse=True)
    ]

    # 5. Day-by-Day Spending Velocity & Cumulative Burn
    # Group expense amounts by exact date
    daily_map = {}
    for t in month_tx:
        if t.get("type") == "expense":
            d = t.get("date", "")
            daily_map[d] = daily_map.get(d, 0.0) + t.get("amount", 0.0)

    sorted_days = sorted(daily_map.keys())
    daily_trends = []
    running_cum = 0.0
    for d in sorted_days:
        amt = daily_map[d]
        running_cum += amt
        daily_trends.append({
            "date": d,
            "day": d[-2:],
            "amount": amt,
            "cumulative": running_cum
        })

    # 6. Multi-Month Trend History (Comparing all available months)
    monthly_history = []
    for m in sorted(all_months):
        m_items = [t for t in all_tx if t.get("date", "").startswith(m)]
        inc = sum(t["amount"] for t in m_items if t.get("type") == "income")
        exp = sum(t["amount"] for t in m_items if t.get("type") == "expense")
        monthly_history.append({
            "month": m,
            "income": inc,
            "expense": exp,
            "savings": inc - exp
        })

    return {
        "available_months": all_months,
        "selected_month": selected_month,
        "summary": {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_savings": net_savings,
            "savings_rate": savings_rate,
            "transaction_count": len(month_tx),
            "daily_average": round(total_expense / max(1, len(sorted_days)), 1)
        },
        "daily_trends": daily_trends,
        "category_breakdown": category_breakdown,
        "payment_methods": payment_methods,
        "monthly_history": monthly_history
    }

