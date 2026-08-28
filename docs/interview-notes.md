# AgentShield Interview Preparation Notes

This document contains concise, technical, and architectural explanations for common interview questions related to the AgentShield application design, CognoDB integration, and graph security modeling.

---

### 1. Why use a graph database for security auditing?
Security risk in modern AI agent architectures is fundamentally about **relationships** and **indirect access pathways** rather than isolated database tables. 
An agent might seem secure in isolation, but through its tools, it can trigger APIs that access highly sensitive databases.
In a relational database, finding these multi-hop traversal paths requires complex, recursive Common Table Expressions (CTEs) or deep chains of SQL `JOIN` statements that are computationally expensive, hard to read, and difficult to maintain. A graph database natively treats entities (Agents, Tools, APIs, DataSources) as nodes, and access privileges as edges, allowing O(1) traversal across multiple hops.

---

### 2. Why CognoDB?
**CognoDB** is a developer-friendly graph database that exposes the industry-standard **openCypher** query language over the high-performance **Bolt protocol**. Using CognoDB allows us to implement expressively structured queries while benefiting from a fully managed graph service.

---

### 3. Why the official Neo4j Python Driver?
CognoDB is fully compatible with the Bolt protocol. By using the official `neo4j` Python driver rather than a proprietary SDK, we:
1. Adhere to open standards (Bolt / openCypher).
2. Avoid vendor lock-in.
3. Leverage a highly optimized, thread-safe connection-pooling client that is widely adopted in enterprise production environments.

---

### 4. Explain the Graph Data Model
Our model maps the security surface using:
* **Nodes**: `Agent`, `Tool`, `API`, `DataSource`, `Permission`, `Policy`, and `Secret`.
* **Relationships**:
  * `Agent -[:USES]-> Tool` (execution routing)
  * `Tool -[:CALLS]-> API` (network integration routing)
  * `API -[:ACCESSES]-> DataSource` (data persistence routing)
  * `Agent -[:HAS_PERMISSION]-> Permission -[:ALLOWS]-> DataSource` (direct authorization)
  * `Agent -[:HAS_SECRET]-> Secret` (credential exposure)
  * `Agent -[:GOVERNED_BY]-> Policy` (governance containment)

---

### 5. What is a multi-hop traversal?
A multi-hop traversal is the process of navigating across multiple consecutive relationships in the graph. For example, verifying what databases an Agent can reach requires traversing three hops:
$$\text{Agent} \xrightarrow{\text{USES}} \text{Tool} \xrightarrow{\text{CALLS}} \text{API} \xrightarrow{\text{ACCESSES}} \text{DataSource}$$
In Cypher, this is expressed elegantly as a single pattern matching statement:
```cypher
MATCH (a:Agent {id: $agent_id})-[:USES]->(t)-[:CALLS]->(api)-[:ACCESSES]->(d:DataSource)
RETURN d
```

---

### 6. Which query is difficult or awkward in a relational model?
**Policy Violation Detection** and **Full Access Path discovery**.
If we need to check if *any* customer-facing agent can indirectly access payroll data, a SQL query would need to join:
`agents` $\bowtie$ `agent_tools` $\bowtie$ `tools` $\bowtie$ `tool_apis` $\bowtie$ `apis` $\bowtie$ `api_datasources` $\bowtie$ `datasources`.
If the length of the path is variable (e.g., if a tool can call another tool, or permissions can be inherited through groups), SQL requires recursive CTEs which are slow and unreadable. In Cypher, variable-length paths are queried trivially using `-[*1..5]->`.

---

### 7. How is the Blast Radius calculated?
We calculate blast radius by tracing downstream dependencies.
* For a **Tool**: We find all `Agents` that call the tool (who would be affected if the tool is hijacked), all `APIs` it makes requests to, and all `DataSources` accessed by those APIs.
* For an **Agent**: We find all connected tools, exposed secrets, reachable APIs, and data sources (either via tool execution or via direct permissions).

---

### 8. How is the Risk Scored?
We use a deterministic, explainable risk scoring system (0–100) instead of an opaque ML model:
1. **Data Sensitivity (Max 40)**: Based on the highest sensitivity level of reachable DataSources (Highly Sensitive = 40, Restricted = 25, Confidential = 15, Internal = 5, Public = 0).
2. **Tool Risk (Max 30)**: Highest risk level of tools used (Critical = 30, High = 20, Medium = 10, Low = 0).
3. **Blast Radius (Max 10)**: +1 point per reachable API/DataSource, capped at 10.
4. **Policy Violations (Max 20)**: +10 points per violated policy, capped at 20.
5. **Exposed Secrets (Max 10)**: +10 points if the agent has high/critical exposure secrets.

---

### 9. How does Policy Violation Detection work?
Violations are patterns detected in Cypher. Policies define constraints (e.g. `forbidden_categories: ["HR", "Financial"]`).
The backend executes a query checking if:
`(:Policy)<-[:GOVERNED_BY]-(:Agent)-[:USES]->(:Tool)-[:CALLS]->(:API)-[:ACCESSES]->(d:DataSource)`
where `d.category` or `d.sensitivity` is in the policy's forbidden sets. The graph query returns the violating node chain, which we render horizontally in the UI.

---

### 10. How are secrets protected?
1. **Environment Variables**: No credentials (URI, username, password, OpenAI keys) are hardcoded in the codebase. They are loaded at startup using `python-dotenv`.
2. **Ignored Configuration**: `.env` is explicitly added to `.gitignore`.
3. **Backend Isolation**: Credentials and keys are processed purely on the FastAPI server and never sent to the React frontend.

---

### 11. How does the application handle database failure?
We implement graceful degradation:
* At startup, the API checks connectivity. If offline, it logs warnings and starts degraded.
* The `/health` endpoint checks database connectivity and returns a `"status": "degraded"` block.
* Endpoints return a structured `500 Connection Error` rather than crashing the process.
* The React frontend handles `500` errors by rendering a clean connection warning card with a **Retry** button, preventing blank screen crashes.

---

### 12. What would you improve in production?
1. **Role-Based Access Control (RBAC)**: Implement OAuth2 on FastAPI endpoints so only authorized security analysts can query risk paths.
2. **Graph Caching**: Cache computed risk scores in Redis, invalidating them only when the graph topology changes.
3. **Real-time Event Ingestion**: Feed logs from Agent execution engines directly into the graph via Kafka, dynamically updating risk scores as agents call new tools.
