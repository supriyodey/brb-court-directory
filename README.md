# Modern US Court & Public Records Directory (BRB Publications Clone)

An automated, modern minimalist public record directory holding records of every court **Public Access Terminal (PAT)**, phone numbers, clerk emails, physical addresses, online docket search links, and fee schedules across all **50 US States and 3,143+ Counties**.

Powered by **Nebius AI Studio** (high-throughput structured LLM extraction) and **Tavily Search API** (targeted web discovery) to verify and update records automatically on scheduled intervals without human intervention.

---

## 🌟 Key Features

- **50 US States & Counties Coverage**: Full directory breakdown filterable by State (CA, NY, TX, FL, IL, etc.) and County Name.
- **Public Access Terminals (PAT) Tracking**: Tracks onsite terminal counts, access hours, workstation fees, and special onsite inspection policies.
- **Nebius AI + Tavily Autonomous Pipeline**: 
  - **Tavily** discovers updated county clerk domains (`.gov`, `.us`).
  - **Nebius** (Llama 3.3 / Qwen 2.5) extracts structured JSON data (phones, emails, PAT specs).
  - **Diff Engine** logs updated fields and maintains a verification audit log.
- **Minimalist Swiss-Style UI**: Ultra-clean, high-contrast typography, state selector pills, instant search, PAT toggle, and detail modal.

---

## 🚀 Quick Start

### Running the Directory Server
```bash
C:\Users\devsu\AppData\Local\Programs\Python\Python313\python.exe run.py
```
Open **`http://127.0.0.1:8000`** in your web browser.

---

## ⚙️ Configuration & Environment Variables

Create a `.env` file or provide API keys directly in the web UI's **Auto-Sync Control** panel:

```env
NEBIUS_API_KEY=your_nebius_studio_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

## 📊 API Endpoints

- `GET /api/states`: List 50 US States with court counts and PAT coverage percentages.
- `GET /api/states/{state_id}/counties`: List all counties in a state.
- `GET /api/courts`: Filter courts by state, county, court type, PAT availability, or search term.
- `GET /api/courts/{court_id}`: Retrieve detailed court record with full PAT guidelines and fees.
- `POST /api/sync/trigger`: Trigger automated verification scan using Nebius AI + Tavily pipeline.
- `GET /api/sync/logs`: View recent field updates and verification audit history.
