from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import PlainTextResponse
from app.models import HistoricalDataPayload
from app.database import get_history_collection
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/history", tags=["Historical Data & CSV"])


@router.get("", response_model=HistoricalDataPayload)
async def get_history(current_user: dict = Depends(get_current_user)):
    """
    Get saved historical monthly dataset for current user.
    """
    hist_col = get_history_collection()
    if hist_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    doc = await hist_col.find_one({"user_id": current_user["id"]})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No historical dataset found for this user."
        )

    return HistoricalDataPayload(
        labels=doc.get("labels", []),
        mn=doc.get("mn", []),
        cats=doc.get("cats", {}),
        income=doc.get("income", [])
    )


@router.post("/sync")
async def sync_history(
    payload: HistoricalDataPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Save or update user's historical dataset in MongoDB.
    """
    hist_col = get_history_collection()
    if hist_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available."
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    doc = {
        "user_id": current_user["id"],
        "labels": payload.labels,
        "mn": payload.mn,
        "cats": payload.cats,
        "income": payload.income,
        "updated_at": now_iso
    }

    await hist_col.update_one(
        {"user_id": current_user["id"]},
        {"$set": doc},
        upsert=True
    )
    return {"message": "Historical data synced to MongoDB successfully.", "months_count": len(payload.labels)}


@router.get("/template.csv", response_class=PlainTextResponse)
async def download_sample_csv():
    """
    Provides sample CSV data format for user download.
    """
    csv_content = """date,category,amount,income
2024-01-01,Rent,12000,45000
2024-01-01,Food,6000,45000
2024-01-01,Transport,2500,45000
2024-01-01,Utilities,2000,45000
2024-01-01,Entertainment,3000,45000
2024-01-01,Shopping,3500,45000
2024-01-01,EMI,5000,45000
2024-01-01,Health,1000,45000
2024-02-01,Rent,12000,45000
2024-02-01,Food,6200,45000
2024-02-01,Transport,2400,45000
2024-02-01,Utilities,2100,45000
2024-02-01,Entertainment,2800,45000
2024-02-01,Shopping,3200,45000
2024-02-01,EMI,5000,45000
2024-02-01,Health,1100,45000
2024-03-01,Rent,12000,48000
2024-03-01,Food,6400,48000
2024-03-01,Transport,2600,48000
2024-03-01,Utilities,2000,48000
2024-03-01,Entertainment,3100,48000
2024-03-01,Shopping,3600,48000
2024-03-01,EMI,5000,48000
2024-03-01,Health,1000,48000
2024-04-01,Rent,12000,48000
2024-04-01,Food,6100,48000
2024-04-01,Transport,2500,48000
2024-04-01,Utilities,2200,48000
2024-04-01,Entertainment,3300,48000
2024-04-01,Shopping,3400,48000
2024-04-01,EMI,5000,48000
2024-04-01,Health,1200,48000
2024-05-01,Rent,12000,48000
2024-05-01,Food,6300,48000
2024-05-01,Transport,2550,48000
2024-05-01,Utilities,2150,48000
2024-05-01,Entertainment,3200,48000
2024-05-01,Shopping,3700,48000
2024-05-01,EMI,5000,48000
2024-05-01,Health,1000,48000
2024-06-01,Rent,12000,48000
2024-06-01,Food,6500,48000
2024-06-01,Transport,2600,48000
2024-06-01,Utilities,2100,48000
2024-06-01,Entertainment,3400,48000
2024-06-01,Shopping,3800,48000
2024-06-01,EMI,5000,48000
2024-06-01,Health,1300,48000
"""
    return PlainTextResponse(
        content=csv_content.strip(),
        headers={"Content-Disposition": "attachment; filename=budget_template.csv"}
    )
