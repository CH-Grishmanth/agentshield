import logging
from backend import config
from openai import OpenAI

logger = logging.getLogger(__name__)

def generate_risk_explanation(path_nodes: list, policy_details: dict = None, risk_score: int = 0) -> str:
    """
    Generates a natural language explanation of a risky graph access path.
    Uses OpenAI if OPENAI_API_KEY is configured, otherwise falls back to a 
    structured rule-based explanation engine.
    """
    if config.OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            path_desc = " -> ".join([f"[{n.get('label')}: {n.get('name')}]" for n in path_nodes])
            
            prompt = f"""
            As a cybersecurity AI agent and security graph architect, explain the risk associated with this access path:
            Path: {path_desc}
            Risk Score: {risk_score}/100
            Governing Policy: {policy_details.get('name') if policy_details else 'None'}
            Policy Description: {policy_details.get('description') if policy_details else 'None'}
            
            Provide a short, professional, and actionable security explanation (2-3 sentences) detailing:
            1. Why this is dangerous (e.g. indirect access, tool compromise, policy violation).
            2. The potential impact (e.g. data breach, credentials leak).
            3. A recommended remediation.
            Do not write markdown headers, keep it concise.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional security compliance officer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate explanation using OpenAI: {e}. Falling back to rule-based explanation.")

    # Rule-based fallback engine (Deterministic)
    agent = next((n for n in path_nodes if n.get('label') == 'Agent'), {})
    tool = next((n for n in path_nodes if n.get('label') == 'Tool'), {})
    api = next((n for n in path_nodes if n.get('label') == 'API'), {})
    ds = next((n for n in path_nodes if n.get('label') == 'DataSource'), {})
    
    explanation = f"Security Analysis: The agent '{agent.get('name', 'Unknown')}' is capable of reaching the resource '{ds.get('name', 'Unknown')}' "
    
    if ds.get("sensitivity") in ["Highly Sensitive", "Restricted"]:
        explanation += f"which is classified as '{ds.get('sensitivity')}' (high risk). "
    else:
        explanation += f"classified as '{ds.get('sensitivity')}' sensitivity. "
        
    if tool and api:
        explanation += f"This access is indirect: the Agent uses the tool '{tool.get('name')}' which executes calls through '{api.get('name')}' to access the database. "
    else:
        permission = next((n for n in path_nodes if n.get('label') == 'Permission'), {})
        if permission:
            explanation += f"This access is authorized by the direct permission '{permission.get('name')}' allowing access to the data store. "
        else:
            explanation += f"This access occurs via a direct path in the graph. "
            
    if policy_details:
        explanation += (
            f"This creates a policy violation against '{policy_details.get('name')}', which forbids access "
            f"to resources of sensitivity/category matching forbidden targets for this class of agent. "
        )
        
    explanation += (
        f"Remediation: Enforce least privilege by removing unnecessary tool USES relationships, "
        f"or configure firewalls on API '{api.get('name')}' to prevent unauthorized traversal."
        if api else
        f"Remediation: Revoke the permission '{permission.get('name', 'entitlement')}' to sever this direct access route."
    )
    
    return explanation
