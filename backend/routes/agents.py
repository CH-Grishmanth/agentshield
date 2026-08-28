from fastapi import APIRouter, HTTPException
from typing import List
from backend.database import get_driver
from backend.queries import cypher_queries
from backend.services import risk_service, llm_service
from backend.models.schemas import (
    AgentSchema, AgentDetailsResponse, DataSourceSchema, 
    RiskyPathResponse, ExplanationRequest, ExplanationResponse
)

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.get("", response_model=List[AgentSchema])
def list_agents():
    driver = get_driver()
    if not driver:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
    try:
        with driver.session() as session:
            return session.execute_read(cypher_queries.get_agents_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{agent_id}", response_model=AgentDetailsResponse)
def get_agent_details(agent_id: str):
    driver = get_driver()
    if not driver:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
    try:
        with driver.session() as session:
            details = session.execute_read(cypher_queries.get_agent_details, agent_id)
            if not details:
                raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found.")
            
            # Compute risk score dynamically
            risk_score = session.execute_read(risk_service.calculate_agent_risk_score, agent_id)
            details["risk_score"] = risk_score
            return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{agent_id}/reachable-resources", response_model=List[DataSourceSchema])
def get_reachable_resources(agent_id: str):
    driver = get_driver()
    if not driver:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
    try:
        with driver.session() as session:
            # First check if agent exists
            exists = session.execute_read(cypher_queries.get_agent_details, agent_id)
            if not exists:
                raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found.")
            return session.execute_read(cypher_queries.get_reachable_datasources, agent_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{agent_id}/risk-paths", response_model=List[RiskyPathResponse])
def get_risky_paths(agent_id: str):
    driver = get_driver()
    if not driver:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
    try:
        with driver.session() as session:
            exists = session.execute_read(cypher_queries.get_agent_details, agent_id)
            if not exists:
                raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found.")
            return session.execute_read(cypher_queries.get_risky_access_paths, agent_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/explain-risk", response_model=ExplanationResponse)
def explain_risk(req: ExplanationRequest):
    try:
        explanation = llm_service.generate_risk_explanation(
            path_nodes=req.path_nodes,
            policy_details=req.policy_details,
            risk_score=req.risk_score
        )
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")
