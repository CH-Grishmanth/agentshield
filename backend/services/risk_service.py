import logging
from backend.queries import cypher_queries

logger = logging.getLogger(__name__)

def calculate_agent_risk_score(tx, agent_id: str) -> dict:
    """
    Calculates a transparent, explainable risk score for an agent based on:
    1. Maximum sensitivity of reachable data sources (up to 30 pts).
    2. Highest risk level of tools used (up to 25 pts).
    3. Number of reachable APIs and DataSources (blast radius - up to 15 pts).
    4. Policy violations (up to 20 pts).
    5. Exposed secrets (up to 10 pts).
    
    Total score is capped at 100.
    """
    agent_details = cypher_queries.get_agent_details(tx, agent_id)
    if not agent_details:
        return {
            "score": 0, "level": "Low",
            "factors": {"data_sensitivity": 0, "tool_risk": 0, "blast_radius": 0, "policy_violations": 0, "exposed_secrets": 0},
            "breakdown": {}
        }
        
    reachable_ds = cypher_queries.get_reachable_datasources(tx, agent_id)
    high_sensitivity_ds = cypher_queries.get_high_sensitivity_resources(tx, agent_id)
    
    # 1. Data Sensitivity Score (Max: 30)
    # Sensitivities: Highly Sensitive (30), Restricted (20), Confidential (10), Internal (5), Public/None (0)
    sensitivity_points = 0
    max_sensitivity = "Public"
    all_reachable = reachable_ds + high_sensitivity_ds
    
    sensitivities_map = {
        "Highly Sensitive": 30,
        "Restricted": 20,
        "Confidential": 10,
        "Internal": 5,
        "Public": 0
    }
    
    for ds in all_reachable:
        sens = ds.get("sensitivity", "Public")
        pts = sensitivities_map.get(sens, 0)
        if pts > sensitivity_points:
            sensitivity_points = pts
            max_sensitivity = sens
            
    # 2. Tool Risk Score (Max: 25)
    # Risk levels: Critical (25), High (15), Medium (8), Low (0)
    tool_points = 0
    max_tool_risk = "Low"
    tool_risk_map = {
        "Critical": 25,
        "High": 15,
        "Medium": 8,
        "Low": 0
    }
    
    for tool in agent_details["tools"]:
        risk = tool.get("risk_level", "Low")
        pts = tool_risk_map.get(risk, 0)
        if pts > tool_points:
            tool_points = pts
            max_tool_risk = risk
            
    # 3. Blast Radius Impact (Max: 15)
    # 1.5 points per reachable DataSource or API (capped at 15 pts)
    blast_radius = cypher_queries.get_agent_blast_radius(tx, agent_id)
    blast_points = 0
    num_affected_ds = 0
    num_affected_apis = 0
    if blast_radius:
        num_affected_ds = len(blast_radius.get("affected_datasources", []))
        num_affected_apis = len(blast_radius.get("affected_apis", []))
        # 1.5 points per resource, up to 15
        blast_points = min(15.0, (num_affected_ds * 1.5) + (num_affected_apis * 1.5))
        # Round to integer for clean reporting
        blast_points = int(round(blast_points))
        
    # 4. Policy Violations (Max: 20)
    # Fetch all violations and count how many belong to this agent
    all_violations = cypher_queries.get_policy_violations(tx)
    agent_violations = [v for v in all_violations if v["agent"]["id"] == agent_id]
    violation_points = min(20, len(agent_violations) * 10) # 10 pts per violation, capped at 20
    
    # 5. Exposed Secrets (Max: 10)
    # Count secrets held by the agent. High/Critical exposure secrets add 5 points each.
    secret_points = 0
    secrets_held = agent_details["secrets"]
    for s in secrets_held:
        exp = s.get("exposure_level", "Low")
        if exp in ["High", "Critical"]:
            secret_points += 5
            
    secret_points = min(10, secret_points)
    
    # Total Score Calculation
    total_score = sensitivity_points + tool_points + blast_points + violation_points + secret_points
    total_score = min(100, int(total_score))
    
    # Determine Risk Level Category (New thresholds: 0-24 Low, 25-49 Med, 50-74 High, 75-100 Crit)
    if total_score >= 75:
        risk_level = "Critical"
    elif total_score >= 50:
        risk_level = "High"
    elif total_score >= 25:
        risk_level = "Medium"
    else:
        risk_level = "Low"
        
    return {
        "score": total_score,
        "level": risk_level,
        "factors": {
            "data_sensitivity": int(sensitivity_points),
            "tool_risk": int(tool_points),
            "blast_radius": int(blast_points),
            "policy_violations": int(violation_points),
            "exposed_secrets": int(secret_points)
        },
        "breakdown": {
            "max_sensitivity": max_sensitivity,
            "max_tool_risk": max_tool_risk,
            "reachable_datasources_count": num_affected_ds,
            "reachable_apis_count": num_affected_apis,
            "policy_violations_count": len(agent_violations),
            "exposed_secrets_count": len(secrets_held)
        }
    }
