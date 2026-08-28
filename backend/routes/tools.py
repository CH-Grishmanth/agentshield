from fastapi import APIRouter, HTTPException
from typing import List
from backend.database import get_driver
from backend.queries import cypher_queries
from backend.models.schemas import ToolSchema, ToolBlastRadiusResponse, AgentBlastRadiusResponse

router = APIRouter(prefix="", tags=["Tools / Blast Radius"])

@router.get("/tools", response_model=List[ToolSchema])
def list_tools():
    driver = get_driver()
    if not driver:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
    try:
        with driver.session() as session:
            return session.execute_read(cypher_queries.get_tools_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/tools/{tool_id}/blast-radius", response_model=ToolBlastRadiusResponse)
def get_tool_blast_radius(tool_id: str):
    driver = get_driver()
    if not driver:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
    try:
        with driver.session() as session:
            radius = session.execute_read(cypher_queries.get_tool_blast_radius, tool_id)
            if not radius:
                raise HTTPException(status_code=404, detail=f"Tool with ID '{tool_id}' not found.")
            return radius
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/agents/{agent_id}/blast-radius", response_model=AgentBlastRadiusResponse)
def get_agent_blast_radius(agent_id: str):
    driver = get_driver()
    if not driver:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
    try:
        with driver.session() as session:
            radius = session.execute_read(cypher_queries.get_agent_blast_radius, agent_id)
            if not radius:
                raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found.")
            return radius
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
