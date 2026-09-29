from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class StateBase(BaseModel):
    id: str
    name: str
    fips_code: Optional[str] = None
    region: Optional[str] = None

    class Config:
        from_attributes = True

class CountyBase(BaseModel):
    id: int
    state_id: str
    name: str
    fips_code: Optional[str] = None
    county_seat: Optional[str] = None

    class Config:
        from_attributes = True

class CourtBase(BaseModel):
    id: int
    county_id: int
    name: str
    court_type: str
    address: Optional[str] = None
    city: str
    zip_code: Optional[str] = None
    main_phone: Optional[str] = None
    clerk_phone: Optional[str] = None
    records_phone: Optional[str] = None
    email: Optional[str] = None
    website_url: Optional[str] = None
    online_search_url: Optional[str] = None
    
    # PAT Details
    has_pat: bool
    pat_hours: Optional[str] = None
    pat_terminal_count: Optional[int] = 0
    pat_fee_info: Optional[str] = None
    pat_notes: Optional[str] = None
    
    access_status: str
    copy_fee_per_page: Optional[float] = None
    certified_copy_fee: Optional[float] = None
    
    last_verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True

class CourtDetail(CourtBase):
    county_name: Optional[str] = None
    state_name: Optional[str] = None
    state_id: Optional[str] = None

class SyncTriggerRequest(BaseModel):
    court_id: Optional[int] = None
    county_id: Optional[int] = None
    state_id: Optional[str] = None
    force_refresh: bool = False

class NebiusExtractionSchema(BaseModel):
    main_phone: Optional[str] = Field(None, description="Primary court phone number")
    clerk_phone: Optional[str] = Field(None, description="Direct court clerk phone number")
    records_phone: Optional[str] = Field(None, description="Records department phone number")
    email: Optional[str] = Field(None, description="Official court or clerk email address")
    website_url: Optional[str] = Field(None, description="Official court website URL")
    online_search_url: Optional[str] = Field(None, description="Case search or docket search portal link")
    has_pat: bool = Field(True, description="Whether Public Access Terminals (PAT) are available on-site")
    pat_hours: Optional[str] = Field(None, description="Onsite PAT terminal access hours")
    pat_terminal_count: Optional[int] = Field(2, description="Number of public access terminals available")
    pat_fee_info: Optional[str] = Field(None, description="PAT inspection and printing fee details")
    pat_notes: Optional[str] = Field(None, description="Special notes or guidelines for onsite PAT users")
