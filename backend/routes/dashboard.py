from fastapi import APIRouter, HTTPException
from backend.database import get_driver
from backend.queries import cypher_queries
from backend.models.schemas import DashboardStatsResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardStatsResponse)
def get_stats():
    driver = get_driver()
    if not driver:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
        
    try:
        with driver.session() as session:
            stats = session.execute_read(cypher_queries.get_dashboard_stats)
            return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
