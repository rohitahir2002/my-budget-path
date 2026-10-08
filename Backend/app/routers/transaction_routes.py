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
