from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import projects, phases, approvals, ai_copilot, users, integrations, chat, auth
from app.database import engine, Base
from app import models, models_integrations  # Import all models

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TAO SDLC API",
    description="AI-Augmented Software Development Lifecycle Management System",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tao-sdlc-automation-yq3j.vercel.app",
        "https://historiographical-uninjuriously-doreatha.ngrok-free.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(phases.router, prefix="/api/phases", tags=["Phases"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(ai_copilot.router, prefix="/api/ai", tags=["AI Copilot"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat"])

@app.get("/")
async def root():
    return {
        "message": "TAO SDLC API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

