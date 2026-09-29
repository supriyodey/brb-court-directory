import os
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from ..models import SyncLog, Court
from ..schemas import SyncTriggerRequest
from ..services.updater_service import CourtUpdaterEngine

router = APIRouter(prefix="/api/sync", tags=["sync"])

@router.post("/trigger")
async def trigger_sync(
    payload: SyncTriggerRequest,
    x_nebius_key: Optional[str] = Header(None),
    x_tavily_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Triggers the Nebius AI + Tavily Search automated court verification pipeline
    for a specific court_id, county_id, or state_id.
    """
    nebius_key = x_nebius_key or os.getenv("NEBIUS_API_KEY")
    tavily_key = x_tavily_key or os.getenv("TAVILY_API_KEY")

    engine = CourtUpdaterEngine(db=db, nebius_key=nebius_key, tavily_key=tavily_key)

    if payload.court_id:
        res = await engine.verify_and_update_court(payload.court_id)
        return {"mode": "single_court", "data": res}
    elif payload.county_id:
        res = await engine.batch_sync_county(payload.county_id)
        return {"mode": "county_batch", "data": res}
    else:
        # Default: pick first 3 courts that haven't been verified recently
        courts = db.query(Court).order_by(Court.last_verified_at.asc()).limit(3).all()
        results = []
        for c in courts:
            r = await engine.verify_and_update_court(c.id)
            results.append(r)
        return {"mode": "auto_batch", "processed_courts": len(results), "data": results}

@router.get("/logs")
def get_sync_logs(limit: int = 20, db: Session = Depends(get_db)):
    logs = db.query(SyncLog).order_by(SyncLog.executed_at.desc()).limit(limit).all()
    output = []
    for log in logs:
        court = db.query(Court).filter(Court.id == log.court_id).first()
        output.append({
            "id": log.id,
            "court_id": log.court_id,
            "court_name": court.name if court else "Unknown Court",
            "executed_at": log.executed_at.isoformat(),
            "status": log.status,
            "source_url": log.source_url,
            "changed_fields": log.changed_fields
        })
    return output
