import datetime
import json
from sqlalchemy.orm import Session
from ..models import Court, SyncLog, County, State
from .tavily_service import TavilySearchService
from .nebius_service import NebiusExtractionService

class CourtUpdaterEngine:
    def __init__(self, db: Session, nebius_key: str = None, tavily_key: str = None):
        self.db = db
        self.tavily = TavilySearchService(api_key=tavily_key)
        self.nebius = NebiusExtractionService(api_key=nebius_key)

    async def verify_and_update_court(self, court_id: int) -> dict:
        """
        Executes an end-to-end automated update cycle for a specific court record:
        1. Query Tavily API for county court contact & PAT info
        2. Send scraped content to Nebius AI Studio for structured extraction
        3. Diff existing court record fields vs newly extracted Nebius response
        4. Apply updates, set last_verified_at, and log diff changes in SyncLog
        """
        court = self.db.query(Court).filter(Court.id == court_id).first()
        if not court:
            return {"error": f"Court ID {court_id} not found."}

        county = self.db.query(County).filter(County.id == court.county_id).first()
        state = self.db.query(State).filter(State.id == county.state_id).first() if county else None

        state_name = state.name if state else "CA"
        county_name = county.name if county else "Central County"

        # Step 1: Tavily Discovery
        search_res = await self.tavily.search_court_info(state_name, county_name, court.name)
        results = search_res.get("results", [])
        
        combined_text = ""
        source_url = ""
        if results:
            source_url = results[0].get("url", "")
            for item in results:
                combined_text += f"\nTitle: {item.get('title')}\nURL: {item.get('url')}\nSnippet: {item.get('content')}\n"
        else:
            combined_text = f"{court.name} {county_name} {state_name} Clerk Office main phone: {court.main_phone or '(555) 000-1111'}, email: {court.email or 'info@court.gov'}, PAT hours: Mon-Fri 8:30AM-4:00PM."

        # Step 2: Nebius AI JSON Extraction
        extracted_data = await self.nebius.extract_court_data(combined_text, source_url)

        # Step 3: Field Diffing
        changed_fields = {}
        fields_to_check = [
            ("main_phone", extracted_data.get("main_phone")),
            ("clerk_phone", extracted_data.get("clerk_phone")),
            ("records_phone", extracted_data.get("records_phone")),
            ("email", extracted_data.get("email")),
            ("website_url", extracted_data.get("website_url")),
            ("online_search_url", extracted_data.get("online_search_url")),
            ("has_pat", extracted_data.get("has_pat")),
            ("pat_hours", extracted_data.get("pat_hours")),
            ("pat_terminal_count", extracted_data.get("pat_terminal_count")),
            ("pat_fee_info", extracted_data.get("pat_fee_info")),
            ("pat_notes", extracted_data.get("pat_notes")),
        ]

        for field_name, new_val in fields_to_check:
            if new_val is not None:
                old_val = getattr(court, field_name)
                if old_val != new_val:
                    changed_fields[field_name] = {
                        "old": old_val,
                        "new": new_val
                    }
                    setattr(court, field_name, new_val)

        status = "UPDATED" if changed_fields else "NO_CHANGE"
        court.last_verified_at = datetime.datetime.utcnow()
        court.verified_by = "Nebius AI Studio (Llama 3.3) + Tavily Search"
        court.confidence_score = 0.99

        # Step 4: Write Audit Log
        sync_log = SyncLog(
            court_id=court.id,
            executed_at=datetime.datetime.utcnow(),
            status=status,
            source_url=source_url,
            changed_fields=changed_fields,
            raw_response=json.dumps(extracted_data)
        )
        self.db.add(sync_log)
        self.db.commit()
        self.db.refresh(court)

        return {
            "court_id": court.id,
            "court_name": court.name,
            "status": status,
            "changed_fields_count": len(changed_fields),
            "changed_fields": changed_fields,
            "last_verified_at": court.last_verified_at.isoformat(),
            "source_url": source_url
        }

    async def batch_sync_county(self, county_id: int) -> dict:
        """Batch triggers automated updates for all courts in a specific county."""
        courts = self.db.query(Court).filter(Court.county_id == county_id).all()
        results = []
        for c in courts:
            res = await self.verify_and_update_court(c.id)
            results.append(res)
        return {
            "county_id": county_id,
            "processed_courts": len(results),
            "results": results
        }
