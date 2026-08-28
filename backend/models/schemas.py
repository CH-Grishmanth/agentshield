from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AgentSchema(BaseModel):
    id: str
    name: str
    description: str
    category: str
    risk_level: str

class ToolSchema(BaseModel):
    id: str
    name: str
    description: str
    category: str
    risk_level: str

class APISchema(BaseModel):
    id: str
    name: str
    provider: str
    endpoint: str
    risk_level: str

class DataSourceSchema(BaseModel):
    id: str
    name: str
    category: str
    sensitivity: str
    description: str

class PolicySchema(BaseModel):
    id: str
    name: str
    description: str
    severity: str
    forbidden_sensitivities: List[str]
    forbidden_categories: List[str]

class SecretSchema(BaseModel):
    id: str
    name: str
    type: str
    exposure_level: str

class PermissionSchema(BaseModel):
    id: str
    name: str
    scope: str

# Composite schemas for endpoints
class RiskFactorSchema(BaseModel):
    data_sensitivity: int
    tool_risk: int
    blast_radius: int
    policy_violations: int
    exposed_secrets: int

class RiskBreakdownSchema(BaseModel):
    max_sensitivity: str
    max_tool_risk: str
    reachable_datasources_count: int
    reachable_apis_count: int
    policy_violations_count: int
    exposed_secrets_count: int

class RiskScoreSchema(BaseModel):
    score: int
    level: str
    factors: RiskFactorSchema
    breakdown: RiskBreakdownSchema

class AgentDetailsResponse(BaseModel):
    agent: AgentSchema
    tools: List[ToolSchema]
    secrets: List[SecretSchema]
    permissions: List[PermissionSchema]
    policies: List[PolicySchema]
    risk_score: RiskScoreSchema

class DashboardStatsResponse(BaseModel):
    agents: int
    tools: int
    apis: int
    datasources: int
    policies: int
    secrets: int
    risk_distribution: Dict[str, int]

class PolicyViolationResponse(BaseModel):
    policy: PolicySchema
    agent: AgentSchema
    tool: Optional[ToolSchema] = None
    api: Optional[APISchema] = None
    datasource: DataSourceSchema
    path_type: str
    explanation: str

class ToolBlastRadiusResponse(BaseModel):
    tool: ToolSchema
    affected_agents: List[AgentSchema]
    affected_apis: List[APISchema]
    affected_datasources: List[DataSourceSchema]

class AgentBlastRadiusResponse(BaseModel):
    agent: AgentSchema
    affected_tools: List[ToolSchema]
    affected_apis: List[APISchema]
    affected_datasources: List[DataSourceSchema]
    affected_secrets: List[SecretSchema]

class PathNodeSchema(BaseModel):
    id: str
    name: str
    label: str
    risk_level: Optional[str] = None
    sensitivity: Optional[str] = None

class PathRelationshipSchema(BaseModel):
    start: str
    end: str
    type: str

class RiskyPathResponse(BaseModel):
    path_type: str
    nodes: List[PathNodeSchema]
    relationships: List[PathRelationshipSchema]

class ExplanationRequest(BaseModel):
    path_nodes: List[Dict[str, Any]]
    policy_details: Optional[Dict[str, Any]] = None
    risk_score: int

class ExplanationResponse(BaseModel):
    explanation: str

class NetworkNode(BaseModel):
    id: str
    name: str
    label: str
    description: Optional[str] = None
    category: Optional[str] = None
    risk_level: Optional[str] = None
    sensitivity: Optional[str] = None
    provider: Optional[str] = None
    endpoint: Optional[str] = None
    type: Optional[str] = None
    exposure_level: Optional[str] = None
    scope: Optional[str] = None

class NetworkEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str

class NetworkGraphResponse(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
