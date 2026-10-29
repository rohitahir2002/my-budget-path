from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, get_db
from app.routers import (
    auth_routes,
    budget_routes,
    transaction_routes,
    history_routes,
    admin_routes
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    await connect_to_mongo()
    yield
    # Shutdown: Close MongoDB connection
    await close_mongo_connection()


app = FastAPI(
    title="BudgetPath Pro API",
    description="Full-stack AI Budget Planner with MongoDB persistence, JWT Authentication, and RBAC",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits requests from Frontend file or local servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_routes.router)
app.include_router(budget_routes.router)
app.include_router(transaction_routes.router)
app.include_router(history_routes.router)
app.include_router(admin_routes.router)


@app.get("/api/health", tags=["Health"])
@app.get("/health", tags=["Health"], include_in_schema=False)
async def health_check():
    db = get_db()
    db_connected = False
    if db is not None:
        try:
            await db.command("ping")
            db_connected = True
        except Exception:
            db_connected = False

    return {
        "status": "healthy",
        "service": "BudgetPath API",
        "database": "connected" if db_connected else "disconnected (check .env MONGO_URI)"
    }


@app.get("/", tags=["Root"])
@app.get("/api", tags=["Root"], include_in_schema=False)
def root():
    return {
        "app": "BudgetPath Pro API",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "health": "/api/health"
    }
