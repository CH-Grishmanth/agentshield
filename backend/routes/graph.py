from fastapi import APIRouter, HTTPException
from backend.database import get_driver
from backend.queries import cypher_queries
from backend.models.schemas import NetworkGraphResponse

router = APIRouter(prefix="/graph", tags=["Graph Network"])

@router.get("", response_model=NetworkGraphResponse)
def get_graph():
    driver = get_driver()
    if not driver:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
    try:
        with driver.session() as session:
            graph_data = session.execute_read(cypher_queries.get_complete_network)
            return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
