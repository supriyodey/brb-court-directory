from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from ..database import get_db
from ..models import State, County, Court

router = APIRouter(prefix="/api/states", tags=["states"])

@router.get("")
def list_states(db: Session = Depends(get_db)):
    states = db.query(State).order_by(State.name.asc()).all()
    output = []
    
    for st in states:
        county_count = db.query(func.count(County.id)).filter(County.state_id == st.id).scalar()
        court_count = db.query(func.count(Court.id)).join(County).filter(County.state_id == st.id).scalar()
        pat_court_count = db.query(func.count(Court.id)).join(County).filter(
            County.state_id == st.id, Court.has_pat == True
        ).scalar()
        
        output.append({
            "id": st.id,
            "name": st.name,
            "region": st.region,
            "county_count": county_count,
            "court_count": court_count,
            "pat_court_count": pat_court_count,
            "pat_percentage": round((pat_court_count / court_count * 100) if court_count > 0 else 0, 1)
        })
        
    return output

@router.get("/{state_id}/counties")
def list_counties_by_state(state_id: str, db: Session = Depends(get_db)):
    counties = db.query(County).filter(County.state_id == state_id.upper()).order_by(County.name.asc()).all()
    output = []
    
    for c in counties:
        court_count = db.query(func.count(Court.id)).filter(Court.county_id == c.id).scalar()
        pat_count = db.query(func.count(Court.id)).filter(Court.county_id == c.id, Court.has_pat == True).scalar()
        
        output.append({
            "id": c.id,
            "state_id": c.state_id,
            "name": c.name,
            "fips_code": c.fips_code,
            "county_seat": c.county_seat,
            "court_count": court_count,
            "pat_court_count": pat_count
        })
        
    return output
