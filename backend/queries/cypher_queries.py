import logging
from neo4j import Result

logger = logging.getLogger(__name__)

def get_dashboard_stats(tx) -> dict:
    """
    Executes queries to get aggregate counts of all node types and risk distributions.
    """
    query = """
    OPTIONAL MATCH (a:Agent)
    WITH count(distinct a) AS agents
    OPTIONAL MATCH (t:Tool)
    WITH agents, count(distinct t) AS tools
    OPTIONAL MATCH (api:API)
    WITH agents, tools, count(distinct api) AS apis
    OPTIONAL MATCH (d:DataSource)
    WITH agents, tools, apis, count(distinct d) AS datasources
    OPTIONAL MATCH (pol:Policy)
    WITH agents, tools, apis, datasources, count(distinct pol) AS policies
    OPTIONAL MATCH (s:Secret)
    WITH agents, tools, apis, datasources, policies, count(distinct s) AS secrets
    
    OPTIONAL MATCH (a_risk:Agent)
    WITH agents, tools, apis, datasources, policies, secrets,
         sum(case when a_risk.risk_level = 'Critical' then 1 else 0 end) as crit_agents,
         sum(case when a_risk.risk_level = 'High' then 1 else 0 end) as high_agents,
         sum(case when a_risk.risk_level = 'Medium' then 1 else 0 end) as med_agents,
         sum(case when a_risk.risk_level = 'Low' then 1 else 0 end) as low_agents
         
    RETURN agents, tools, apis, datasources, policies, secrets, crit_agents, high_agents, med_agents, low_agents
    """
    result = tx.run(query)
    record = result.single()
    if not record:
        return {
            "agents": 0, "tools": 0, "apis": 0, "datasources": 0, "policies": 0, "secrets": 0,
            "risk_distribution": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        }
    return {
        "agents": record["agents"],
        "tools": record["tools"],
        "apis": record["apis"],
        "datasources": record["datasources"],
        "policies": record["policies"],
        "secrets": record["secrets"],
        "risk_distribution": {
            "Critical": record["crit_agents"] or 0,
            "High": record["high_agents"] or 0,
            "Medium": record["med_agents"] or 0,
            "Low": record["low_agents"] or 0
        }
    }

def get_agents_list(tx) -> list:
    """
    Returns a list of all agents in the database.
    """
    query = """
    MATCH (a:Agent)
    RETURN a ORDER BY a.name
    """
    result = tx.run(query)
    return [dict(record["a"]) for record in result]

def get_agent_details(tx, agent_id: str) -> dict:
    """
    QUERY 1: Find an agent's skills/resources/connections (direct relationships).
    """
    query = """
    MATCH (a:Agent {id: $agent_id})
    OPTIONAL MATCH (a)-[:USES]->(t:Tool)
    OPTIONAL MATCH (a)-[:HAS_SECRET]->(s:Secret)
    OPTIONAL MATCH (a)-[:HAS_PERMISSION]->(perm:Permission)
    OPTIONAL MATCH (a)-[:GOVERNED_BY]->(pol:Policy)
    RETURN a, 
           collect(distinct t) AS tools, 
           collect(distinct s) AS secrets, 
           collect(distinct perm) AS permissions, 
           collect(distinct pol) AS policies
    """
    result = tx.run(query, agent_id=agent_id)
    record = result.single()
    if not record:
        return None
    
    agent_data = dict(record["a"])
    return {
        "agent": agent_data,
        "tools": [dict(t) for t in record["tools"] if t],
        "secrets": [dict(s) for s in record["secrets"] if s],
        "permissions": [dict(p) for p in record["permissions"] if p],
        "policies": [dict(pol) for pol in record["policies"] if pol]
    }

def get_reachable_datasources(tx, agent_id: str) -> list:
    """
    QUERY 2: Find reachable data sources from an agent using multi-hop traversal.
    Path: Agent -> USES -> Tool -> CALLS -> API -> ACCESSES -> DataSource
    """
    query = """
    MATCH (a:Agent {id: $agent_id})-[:USES]->(t:Tool)-[:CALLS]->(api:API)-[:ACCESSES]->(d:DataSource)
    RETURN DISTINCT d
    """
    result = tx.run(query, agent_id=agent_id)
    return [dict(record["d"]) for record in result]

def get_high_sensitivity_resources(tx, agent_id: str) -> list:
    """
    QUERY 3: Find high-sensitivity resources reachable from an agent.
    Includes both execution paths and direct permission paths.
    """
    query = """
    MATCH (a:Agent {id: $agent_id})
    
    // Path 1: Tool execution path
    OPTIONAL MATCH (a)-[:USES]->(t:Tool)-[:CALLS]->(api:API)-[:ACCESSES]->(d1:DataSource)
    WHERE d1.sensitivity IN ['Confidential', 'Restricted', 'Highly Sensitive']
    
    // Path 2: Permission path
    OPTIONAL MATCH (a)-[:HAS_PERMISSION]->(perm:Permission)-[:ALLOWS]->(d2:DataSource)
    WHERE d2.sensitivity IN ['Confidential', 'Restricted', 'Highly Sensitive']
    
    WITH collect(distinct d1) + collect(distinct d2) AS all_ds
    UNWIND all_ds AS ds
    RETURN DISTINCT ds
    """
    result = tx.run(query, agent_id=agent_id)
    return [dict(record["ds"]) for record in result if record["ds"]]

def get_tool_blast_radius(tx, tool_id: str) -> dict:
    """
    QUERY 4: Find blast radius of a tool.
    Returns downstream assets affected if the tool is compromised:
    - Agents using the tool
    - APIs called by the tool
    - DataSources accessed by those APIs
    - Sensitivity levels
    """
    query = """
    MATCH (t:Tool {id: $tool_id})
    OPTIONAL MATCH (a:Agent)-[:USES]->(t)
    OPTIONAL MATCH (t)-[:CALLS]->(api:API)
    OPTIONAL MATCH (api)-[:ACCESSES]->(d:DataSource)
    RETURN t, 
           collect(distinct a) AS affected_agents, 
           collect(distinct api) AS affected_apis, 
           collect(distinct d) AS affected_datasources
    """
    result = tx.run(query, tool_id=tool_id)
    record = result.single()
    if not record:
        return None
    
    tool_data = dict(record["t"])
    return {
        "tool": tool_data,
        "affected_agents": [dict(a) for a in record["affected_agents"] if a],
        "affected_apis": [dict(api) for api in record["affected_apis"] if api],
        "affected_datasources": [dict(d) for d in record["affected_datasources"] if d]
    }

def get_agent_blast_radius(tx, agent_id: str) -> dict:
    """
    Blast radius of an Agent if its credentials/secrets are leaked.
    - Tools it can use
    - APIs it can access
    - DataSources it can access (via execution path or permissions)
    - Secrets exposed
    """
    query = """
    MATCH (a:Agent {id: $agent_id})
    OPTIONAL MATCH (a)-[:USES]->(t:Tool)
    OPTIONAL MATCH (t)-[:CALLS]->(api:API)
    OPTIONAL MATCH (api)-[:ACCESSES]->(d1:DataSource)
    OPTIONAL MATCH (a)-[:HAS_SECRET]->(s:Secret)
    OPTIONAL MATCH (a)-[:HAS_PERMISSION]->(perm:Permission)-[:ALLOWS]->(d2:DataSource)
    RETURN a,
           collect(distinct t) AS affected_tools,
           collect(distinct api) AS affected_apis,
           collect(distinct d1) + collect(distinct d2) AS affected_datasources,
           collect(distinct s) AS affected_secrets
    """
    result = tx.run(query, agent_id=agent_id)
    record = result.single()
    if not record:
        return None
    
    agent_data = dict(record["a"])
    return {
        "agent": agent_data,
        "affected_tools": [dict(t) for t in record["affected_tools"] if t],
        "affected_apis": [dict(api) for api in record["affected_apis"] if api],
        "affected_datasources": [dict(d) for d in record["affected_datasources"] if d],
        "affected_secrets": [dict(s) for s in record["affected_secrets"] if s]
    }

def get_policy_violations(tx) -> list:
    """
    QUERY 5: Find policy violations.
    Identifies if an Agent governed by a Policy can reach a DataSource (via USES->CALLS->ACCESSES or HAS_PERMISSION->ALLOWS)
    where the DataSource sensitivity or category is forbidden by the Policy.
    """
    # 1. Execution path violations
    query_exec = """
    MATCH (pol:Policy)<-[:GOVERNED_BY]-(a:Agent)-[:USES]->(t:Tool)-[:CALLS]->(api:API)-[:ACCESSES]->(d:DataSource)
    WHERE (d.sensitivity IN pol.forbidden_sensitivities) OR (d.category IN pol.forbidden_categories)
    RETURN pol AS policy, a AS agent, t AS tool, api AS api, d AS datasource,
           'execution' AS path_type,
           'Agent ' + a.name + ' uses tool ' + t.name + ' which calls API ' + api.name + ' and accesses forbidden DataSource ' + d.name + ' (' + d.sensitivity + ')' AS explanation
    """
    
    # 2. Permission path violations
    query_perm = """
    MATCH (pol:Policy)<-[:GOVERNED_BY]-(a:Agent)-[:HAS_PERMISSION]->(perm:Permission)-[:ALLOWS]->(d:DataSource)
    WHERE (d.sensitivity IN pol.forbidden_sensitivities) OR (d.category IN pol.forbidden_categories)
    RETURN pol AS policy, a AS agent, null AS tool, null AS api, d AS datasource,
           'permission' AS path_type,
           'Agent ' + a.name + ' has permission ' + perm.name + ' which allows access to forbidden DataSource ' + d.name + ' (' + d.sensitivity + ')' AS explanation
    """
    
    violations = []
    
    res_exec = tx.run(query_exec)
    for record in res_exec:
        violations.append({
            "policy": dict(record["policy"]),
            "agent": dict(record["agent"]),
            "tool": dict(record["tool"]) if record["tool"] else None,
            "api": dict(record["api"]) if record["api"] else None,
            "datasource": dict(record["datasource"]),
            "path_type": record["path_type"],
            "explanation": record["explanation"]
        })
        
    res_perm = tx.run(query_perm)
    for record in res_perm:
        violations.append({
            "policy": dict(record["policy"]),
            "agent": dict(record["agent"]),
            "tool": None,
            "api": None,
            "datasource": dict(record["datasource"]),
            "path_type": record["path_type"],
            "explanation": record["explanation"]
        })
        
    return violations

def get_risky_access_paths(tx, agent_id: str) -> list:
    """
    QUERY 6: Return full risky access paths from an agent to high/critical sensitivity resources.
    Returns path representations including the exact nodes and relationships.
    """
    query_exec = """
    MATCH path = (a:Agent {id: $agent_id})-[:USES]->(t:Tool)-[:CALLS]->(api:API)-[:ACCESSES]->(d:DataSource)
    WHERE d.sensitivity IN ['Highly Sensitive', 'Restricted']
    RETURN path
    """
    query_perm = """
    MATCH path = (a:Agent {id: $agent_id})-[:HAS_PERMISSION]->(perm:Permission)-[:ALLOWS]->(d:DataSource)
    WHERE d.sensitivity IN ['Highly Sensitive', 'Restricted']
    RETURN path
    """
    
    paths_data = []
    
    # Process execution paths
    res_exec = tx.run(query_exec, agent_id=agent_id)
    for record in res_exec:
        path = record["path"]
        nodes_list = []
        relationships_list = []
        
        # Extract node details
        for node in path.nodes:
            nodes_list.append({
                "id": node.get("id"),
                "name": node.get("name"),
                "label": list(node.labels)[0] if node.labels else "Unknown",
                "risk_level": node.get("risk_level"),
                "sensitivity": node.get("sensitivity")
            })
            
        # Extract relationship types
        for rel in path.relationships:
            relationships_list.append({
                "start": rel.start_node.get("id"),
                "end": rel.end_node.get("id"),
                "type": rel.type
            })
            
        paths_data.append({
            "path_type": "execution",
            "nodes": nodes_list,
            "relationships": relationships_list
        })
        
    # Process permission paths
    res_perm = tx.run(query_perm, agent_id=agent_id)
    for record in res_perm:
        path = record["path"]
        nodes_list = []
        relationships_list = []
        
        # Extract node details
        for node in path.nodes:
            nodes_list.append({
                "id": node.get("id"),
                "name": node.get("name"),
                "label": list(node.labels)[0] if node.labels else "Unknown",
                "risk_level": node.get("risk_level"),
                "sensitivity": node.get("sensitivity")
            })
            
        # Extract relationship types
        for rel in path.relationships:
            relationships_list.append({
                "start": rel.start_node.get("id"),
                "end": rel.end_node.get("id"),
                "type": rel.type
            })
            
        paths_data.append({
            "path_type": "permission",
            "nodes": nodes_list,
            "relationships": relationships_list
        })
        
    return paths_data

def get_complete_network(tx) -> dict:
    """
    Fetches all nodes and relationships in the database to render the Graph Explorer.
    """
    query_nodes = "MATCH (n) RETURN n"
    query_rels = "MATCH (n)-[r]->(m) RETURN id(r) as rid, n.id as source, m.id as target, type(r) as type"
    
    nodes_res = tx.run(query_nodes)
    rels_res = tx.run(query_rels)
    
    nodes = []
    for record in nodes_res:
        node = record["n"]
        label = list(node.labels)[0] if node.labels else "Unknown"
        node_dict = dict(node)
        node_dict["label"] = label # Add node type label
        nodes.append(node_dict)
        
    edges = []
    for record in rels_res:
        edges.append({
            "id": str(record["rid"]),
            "source": record["source"],
            "target": record["target"],
            "type": record["type"]
        })
        
    return {"nodes": nodes, "edges": edges}

def get_tools_list(tx) -> list:
    """
    Returns a list of all tools in the database.
    """
    query = """
    MATCH (t:Tool)
    RETURN t ORDER BY t.name
    """
    result = tx.run(query)
    return [dict(record["t"]) for record in result]
