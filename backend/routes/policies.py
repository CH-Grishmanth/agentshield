from fastapi import APIRouter, HTTPException
from typing import List
from backend.database import get_driver
from backend.queries import cypher_queries
from backend.models.schemas import PolicyViolationResponse

router = APIRouter(prefix="/policies", tags=["Policies"])

@router.get("/violations", response_model=List[PolicyViolationResponse])
def get_violations():
    driver = get_driver()
    if not driver:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
    try:
        with driver.session() as session:
            violations = session.execute_read(cypher_queries.get_policy_violations)
            return violations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
