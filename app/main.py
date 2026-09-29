import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .database import engine, Base
from .seed import seed_database
from .api import courts, states, sync

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="US Court & Public Records Directory (BRB Clone)",
    description="Automated court phone, email, and Public Access Terminal (PAT) directory updated via Nebius AI & Tavily",
    version="1.0.0"
)

# Mount Static Files & Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Include API Routers
app.include_router(courts.router)
app.include_router(states.router)
app.include_router(sync.router)

@app.on_event("startup")
def startup_event():
    # Seed database with US States, Counties, and initial Court records
    seed_database()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
