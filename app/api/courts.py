from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Court, County, State, SyncLog
from ..schemas import CourtBase, CourtDetail

router = APIRouter(prefix="/api/courts", tags=["courts"])

@router.get("", response_model=List[CourtDetail])
def list_courts(
    state_id: Optional[str] = Query(None, description="2-letter state code, e.g. CA, NY"),
    county_id: Optional[int] = Query(None, description="County ID"),
    court_type: Optional[str] = Query(None, description="SUPERIOR, DISTRICT, MUNICIPAL, PROBATE, etc."),
    has_pat: Optional[bool] = Query(None, description="Filter courts with Public Access Terminals"),
    search: Optional[str] = Query(None, description="Search term across court name, city, phone, zip"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(
        Court,
        County.name.label("county_name"),
        State.name.label("state_name"),
        State.id.label("state_id")
    ).join(County, Court.county_id == County.id).join(State, County.state_id == State.id)

    if state_id:
        query = query.filter(State.id == state_id.upper())

    if county_id:
        query = query.filter(Court.county_id == county_id)

    if court_type:
        query = query.filter(Court.court_type == court_type.upper())

    if has_pat is not None:
        query = query.filter(Court.has_pat == has_pat)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Court.name.ilike(search_pattern)) |
            (Court.city.ilike(search_pattern)) |
            (Court.main_phone.ilike(search_pattern)) |
            (Court.zip_code.ilike(search_pattern))
        )

    results = query.offset(offset).limit(limit).all()

    output = []
    for court, county_name, state_name, st_id in results:
        detail = CourtDetail.from_orm(court)
        detail.county_name = county_name
        detail.state_name = state_name
        detail.state_id = st_id
        output.append(detail)

    return output

@router.get("/{court_id}", response_model=CourtDetail)
def get_court_detail(court_id: int, db: Session = Depends(get_db)):
    res = db.query(
        Court,
        County.name.label("county_name"),
        State.name.label("state_name"),
        State.id.label("state_id")
    ).join(County, Court.county_id == County.id).join(State, County.state_id == State.id).filter(Court.id == court_id).first()

    if not res:
        raise HTTPException(status_code=404, detail="Court record not found")

    court, county_name, state_name, st_id = res
    detail = CourtDetail.from_orm(court)
    detail.county_name = county_name
    detail.state_name = state_name
    detail.state_id = st_id
    return detail
