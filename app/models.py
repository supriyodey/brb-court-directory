import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .database import Base

class State(Base):
    __tablename__ = "states"

    id = Column(String(2), primary_key=True, index=True) # e.g. "CA", "NY"
    name = Column(String(100), nullable=False, unique=True)
    fips_code = Column(String(5), nullable=True)
    region = Column(String(50), nullable=True)

    counties = relationship("County", back_populates="state", cascade="all, delete-orphan")

class County(Base):
    __tablename__ = "counties"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    state_id = Column(String(2), ForeignKey("states.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    fips_code = Column(String(10), nullable=True)
    county_seat = Column(String(100), nullable=True)

    state = relationship("State", back_populates="counties")
    courts = relationship("Court", back_populates="county", cascade="all, delete-orphan")

class Court(Base):
    __tablename__ = "courts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    court_type = Column(String(50), default="SUPERIOR", index=True) # SUPERIOR, DISTRICT, CIRCUIT, MUNICIPAL, PROBATE, RECORDER, SHERIFF

    # Physical & Mailing Address
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=True)

    # Primary Contact Details
    main_phone = Column(String(50), nullable=True)
    clerk_phone = Column(String(50), nullable=True)
    records_phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    website_url = Column(String(255), nullable=True)
    online_search_url = Column(String(255), nullable=True)

    # Public Access Terminal (PAT) Details
    has_pat = Column(Boolean, default=True, index=True) # Onsite PAT availability
    pat_hours = Column(String(100), nullable=True) # e.g., "Mon-Fri 8:30 AM - 4:00 PM"
    pat_terminal_count = Column(Integer, default=2)
    pat_fee_info = Column(String(255), nullable=True) # e.g., "Free inspection, $0.50/page print"
    pat_notes = Column(Text, nullable=True) # Onsite terminal policies / restrictions

    # Access Status & Fees
    access_status = Column(String(50), default="ONLINE_AND_ONSITE") # ONLINE_AND_ONSITE, ONSITE_PAT_ONLY, ONLINE_ONLY
    copy_fee_per_page = Column(Float, nullable=True, default=0.50)
    certified_copy_fee = Column(Float, nullable=True, default=5.00)

    # Auto-Sync Metadata
    last_verified_at = Column(DateTime, default=datetime.datetime.utcnow)
    verified_by = Column(String(100), default="Nebius AI + Tavily Pipeline")
    confidence_score = Column(Float, default=0.98)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    county = relationship("County", back_populates="courts")
    sync_logs = relationship("SyncLog", back_populates="court", cascade="all, delete-orphan")

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False, index=True)
    executed_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), nullable=False) # "UPDATED", "NO_CHANGE", "FLAGGED"
    source_url = Column(String(255), nullable=True)
    changed_fields = Column(JSON, nullable=True)
    raw_response = Column(Text, nullable=True)

    court = relationship("Court", back_populates="sync_logs")
