from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.database import verify_connection, close_driver
from backend.routes import dashboard, agents, tools, policies, graph

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup behavior: check database connectivity
    connected, msg = verify_connection()
    if connected:
        print(f"Startup API: {msg}")
    else:
        print(f"Startup API WARNING: Database is offline or credentials invalid: {msg}")
    yield
    # Shutdown behavior: close driver resources
    close_driver()

app = FastAPI(
    title="AgentShield API",
    description="Backend service for mapping and auditing AI Agent access paths and policies.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core endpoints
@app.get("/health")
def health_check():
    connected, msg = verify_connection()
    if connected:
        return {"status": "healthy", "database": "connected", "details": msg}
    return {
        "status": "degraded",
        "database": "disconnected",
        "details": msg
    }

# Register API routers
app.include_router(dashboard.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(tools.router, prefix="/api")
app.include_router(policies.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
