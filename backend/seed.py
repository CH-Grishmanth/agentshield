import os
import sys
from pathlib import Path

# Add backend directory to path so we can import from database and config
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.database import get_driver, verify_connection, close_driver

def seed_database():
    driver = get_driver()
    if not driver:
        print("Database not configured. Cannot seed database.")
        sys.exit(1)
        
    print("Clearing existing database contents...")
    with driver.session() as session:
        # Wipe all nodes and relationships
        session.run("MATCH (n) DETACH DELETE n")
    
    print("Seeding new security graph data...")
    with driver.session() as session:
        # 1. Create Agents (22 nodes)
        agents = [
            {"id": "agent-support", "name": "Customer Support Agent", "description": "Automates responses to customer support queries, interacts with public KB and customer details.", "category": "Customer Service", "risk_level": "High"},
            {"id": "agent-hr", "name": "HR Assistant Agent", "description": "Helps HR team manage employee records, onboarding tasks, and resume screening.", "category": "HR", "risk_level": "Medium"},
            {"id": "agent-finance", "name": "Finance Automation Agent", "description": "Performs financial calculations, syncs invoices, and interfaces with the payment gateway.", "category": "Financial", "risk_level": "Medium"},
            {"id": "agent-sales", "name": "Sales Outreach Agent", "description": "Engages with prospective leads and writes metadata to customer CRM.", "category": "Sales", "risk_level": "Low"},
            {"id": "agent-ops", "name": "Infrastructure Operations Agent", "description": "Monitors servers, triggers backups, and handles container configurations.", "category": "Operations", "risk_level": "High"},
            {"id": "agent-marketing", "name": "Marketing Copywriter Agent", "description": "Drafts blogs, posts tweets, and interacts with marketing dashboards.", "category": "Marketing", "risk_level": "Low"},
            {"id": "agent-dev", "name": "Developer Assistant Agent", "description": "Autocompletes code, runs tests, and queries dev servers.", "category": "Development", "risk_level": "High"},
            {"id": "agent-analytics", "name": "Data Analytics Agent", "description": "Queries the database warehouse to produce bi-weekly company performance reports.", "category": "Analytics", "risk_level": "Medium"},
            {"id": "agent-billing", "name": "Billing Agent", "description": "Resolves payment disputes, tracks refunds, and manages stripe metadata.", "category": "Financial", "risk_level": "High"},
            {"id": "agent-chatbot", "name": "Public Website Chatbot", "description": "Direct customer-facing LLM chatbot that answers questions on the public website.", "category": "Public Interface", "risk_level": "Critical"},
            {"id": "agent-security", "name": "Security Compliance Agent", "description": "Audits access logs and checks configuration compliance.", "category": "Security", "risk_level": "Low"},
            {"id": "agent-inventory", "name": "Inventory Management Agent", "description": "Queries warehouse DB to check product availability and update stocks.", "category": "Operations", "risk_level": "Low"},
            {"id": "agent-social", "name": "Social Media Poster Agent", "description": "Automates tweets and posts to buffer queue.", "category": "Marketing", "risk_level": "Low"},
            {"id": "agent-legal", "name": "Contract Reviewer Agent", "description": "Scans PDF contracts and highlights risk clauses for legal approval.", "category": "Legal", "risk_level": "Medium"},
            {"id": "agent-recruiting", "name": "Candidate Screener Agent", "description": "Screens resumes and schedules initial screening calls.", "category": "HR", "risk_level": "Low"},
            {"id": "agent-reporting", "name": "Executive Reporting Agent", "description": "Generates executive summaries on company health.", "category": "Analytics", "risk_level": "Medium"},
            {"id": "agent-translation", "name": "Localisation Agent", "description": "Translates help documents into multiple languages.", "category": "Customer Service", "risk_level": "Low"},
            {"id": "agent-research", "name": "R&D Research Agent", "description": "Searches Wikipedia and internal wiki to support active R&D projects.", "category": "R&D", "risk_level": "Low"},
            {"id": "agent-personal", "name": "Personal Assistant Agent", "description": "Schedules Zoom meetings, updates personal notes.", "category": "General", "risk_level": "Low"},
            {"id": "agent-backup", "name": "Database Backup Agent", "description": "Automated pipeline agent that reads DB and uploads backups to S3.", "category": "Operations", "risk_level": "Medium"},
            {"id": "agent-it-help", "name": "IT Support Desk Agent", "description": "Creates Zendesk tickets and checks server diagnostic logs.", "category": "Customer Service", "risk_level": "Medium"},
            {"id": "agent-audit", "name": "Compliance Auditor Agent", "description": "Governed by compliance guidelines to inspect access patterns.", "category": "Security", "risk_level": "Low"}
        ]
        
        for a in agents:
            session.run(
                "CREATE (a:Agent {id: $id, name: $name, description: $description, category: $category, risk_level: $risk_level})",
                **a
            )
            
        # 2. Create Tools (26 nodes)
        tools = [
            {"id": "tool-crm-read", "name": "CRM Reader", "description": "Reads customer contact logs and sales records.", "category": "API Client", "risk_level": "Low"},
            {"id": "tool-crm-write", "name": "CRM Writer", "description": "Edits customer records and updates status.", "category": "API Client", "risk_level": "Medium"},
            {"id": "tool-email-sender", "name": "Email Sender", "description": "Sends transactional emails to customers via SendGrid.", "category": "API Client", "risk_level": "Medium"},
            {"id": "tool-slack-notifier", "name": "Slack Notifier", "description": "Sends automated alerts to internal Slack channels.", "category": "Communication", "risk_level": "Low"},
            {"id": "tool-payroll-calculator", "name": "Payroll Calculator", "description": "Integrates Workday API to compute bonuses and basic salaries.", "category": "Finance Utility", "risk_level": "High"},
            {"id": "tool-db-reader", "name": "Generic SQL Reader", "description": "Queries custom databases using input SQL strings. High flexibility.", "category": "Database Client", "risk_level": "High"},
            {"id": "tool-shell-executor", "name": "Bash Shell Executor", "description": "Runs local shell commands to modify files or manage processes.", "category": "System Exec", "risk_level": "Critical"},
            {"id": "tool-file-manager", "name": "File System Manager", "description": "Creates, modifies, and deletes local server files.", "category": "System Exec", "risk_level": "High"},
            {"id": "tool-web-search", "name": "Web Search Client", "description": "Queries google search API to retrieve live information.", "category": "API Client", "risk_level": "Low"},
            {"id": "tool-hr-portal", "name": "HR Portal Integration", "description": "Interfaces with HR backend database to query employee records.", "category": "API Client", "risk_level": "Medium"},
            {"id": "tool-weather-api", "name": "Weather Checker", "description": "Queries openweather API.", "category": "API Client", "risk_level": "Low"},
            {"id": "tool-stripe-client", "name": "Stripe Payment Client", "description": "Queries Stripe payments history and processes refunds.", "category": "API Client", "risk_level": "High"},
            {"id": "tool-jira-integrator", "name": "Jira Task Creator", "description": "Creates and updates development tasks.", "category": "API Client", "risk_level": "Low"},
            {"id": "tool-github-client", "name": "GitHub Repository Manager", "description": "Clones, commits and pushes changes to GitHub repositories.", "category": "Developer Tool", "risk_level": "High"},
            {"id": "tool-ssh-client", "name": "SSH Connector", "description": "Executes remote commands on production server environments.", "category": "System Exec", "risk_level": "Critical"},
            {"id": "tool-backup-runner", "name": "Database Backup Runner", "description": "Dumps SQL data and stores in AWS S3 buckets.", "category": "Database Utility", "risk_level": "Medium"},
            {"id": "tool-translator", "name": "Translation Engine", "description": "Translates textual content using DeepL API.", "category": "API Client", "risk_level": "Low"},
            {"id": "tool-analytics-reporter", "name": "SQL Report Generator", "description": "Queries Snowflake warehouse data and prints CSV data sheets.", "category": "Analytics", "risk_level": "Medium"},
            {"id": "tool-social-manager", "name": "Buffer Social Media Client", "description": "Schedules social media posts and updates.", "category": "API Client", "risk_level": "Low"},
            {"id": "tool-legal-scanner", "name": "PDF Contract Reader", "description": "Reads corporate agreements in Google Drive folders.", "category": "File Utility", "risk_level": "Medium"},
            {"id": "tool-resume-parser", "name": "Resume Text Extractor", "description": "Extracts skills and details from uploaded candidate PDFs.", "category": "File Utility", "risk_level": "Low"},
            {"id": "tool-it-ticket-creator", "name": "Zendesk Ticket Integration", "description": "Creates support tickets in zendesk console.", "category": "API Client", "risk_level": "Low"},
            {"id": "tool-log-viewer", "name": "ELK Log Searcher", "description": "Fetches security log files from datadog stream.", "category": "Analytics", "risk_level": "Medium"},
            {"id": "tool-wiki-reader", "name": "Confluence Searcher", "description": "Searches Confluence Wiki database.", "category": "API Client", "risk_level": "Low"},
            {"id": "tool-secret-rotator", "name": "Vault Secret Manager", "description": "Rotates secrets in Hashicorp Vault.", "category": "System Exec", "risk_level": "Critical"},
            {"id": "tool-config-editor", "name": "System Config Editor", "description": "Edits configurations of system microservices.", "category": "System Exec", "risk_level": "High"}
        ]
        
        for t in tools:
            session.run(
                "CREATE (t:Tool {id: $id, name: $name, description: $description, category: $category, risk_level: $risk_level})",
                **t
            )
            
        # 3. Create APIs (30 nodes)
        apis = [
            {"id": "api-salesforce-crm", "name": "Salesforce CRM API", "provider": "Salesforce", "endpoint": "https://api.salesforce.com/v1/crm", "risk_level": "Medium"},
            {"id": "api-stripe-billing", "name": "Stripe Billing Gateway", "provider": "Stripe", "endpoint": "https://api.stripe.com/v3/charges", "risk_level": "High"},
            {"id": "api-hr-api", "name": "Internal HR API", "provider": "Internal", "endpoint": "https://hr.internal.net/api/v1", "risk_level": "Medium"},
            {"id": "api-payroll", "name": "Workday Payroll API", "provider": "Workday", "endpoint": "https://api.workday.com/payroll", "risk_level": "High"},
            {"id": "api-sendgrid", "name": "SendGrid Email API", "provider": "SendGrid", "endpoint": "https://api.sendgrid.com/v3/mail", "risk_level": "Medium"},
            {"id": "api-slack-chat", "name": "Slack Messaging API", "provider": "Slack", "endpoint": "https://slack.com/api/chat.postMessage", "risk_level": "Medium"},
            {"id": "api-aws-s3", "name": "Amazon S3 Bucket API", "provider": "AWS", "endpoint": "https://s3.amazonaws.com/buckets", "risk_level": "High"},
            {"id": "api-jira-cloud", "name": "Jira Cloud REST API", "provider": "Atlassian", "endpoint": "https://api.atlassian.com/jira/v3", "risk_level": "Low"},
            {"id": "api-github-rest", "name": "GitHub REST API", "provider": "GitHub", "endpoint": "https://api.github.com/v3", "risk_level": "High"},
            {"id": "api-ssh-shell", "name": "Server SSH Shell API", "provider": "Internal AWS", "endpoint": "ssh://prod.server.internal", "risk_level": "Critical"},
            {"id": "api-backup-service", "name": "Backup Cloud API", "provider": "Internal AWS", "endpoint": "https://backup.internal.net/api", "risk_level": "Medium"},
            {"id": "api-deepl-translator", "name": "DeepL Translation API", "provider": "DeepL", "endpoint": "https://api.deepl.com/v2/translate", "risk_level": "Low"},
            {"id": "api-snowflake-warehouse", "name": "Snowflake Analytics API", "provider": "Snowflake", "endpoint": "https://snowflake.com/api", "risk_level": "High"},
            {"id": "api-twitter-v2", "name": "Twitter API v2", "provider": "X Corp", "endpoint": "https://api.twitter.com/2/tweets", "risk_level": "Low"},
            {"id": "api-google-drive", "name": "Google Drive Documents API", "provider": "Google", "endpoint": "https://www.googleapis.com/drive/v3", "risk_level": "Medium"},
            {"id": "api-greenhouse-ats", "name": "Greenhouse ATS API", "provider": "Greenhouse", "endpoint": "https://api.greenhouse.io/v1", "risk_level": "Low"},
            {"id": "api-zendesk-support", "name": "Zendesk Tickets API", "provider": "Zendesk", "endpoint": "https://api.zendesk.com/v2", "risk_level": "Low"},
            {"id": "api-datadog-logs", "name": "Datadog Log Streaming API", "provider": "Datadog", "endpoint": "https://api.datadoghq.com/api/v2", "risk_level": "Medium"},
            {"id": "api-confluence-kb", "name": "Confluence Knowledge Base API", "provider": "Atlassian", "endpoint": "https://api.atlassian.com/confluence", "risk_level": "Low"},
            {"id": "api-hashicorp-vault", "name": "Hashicorp Vault Secret API", "provider": "HashiCorp", "endpoint": "https://vault.internal.net/v1", "risk_level": "Critical"},
            {"id": "api-kubernetes-control", "name": "Kubernetes Control API", "provider": "Internal AWS", "endpoint": "https://k8s.internal.net/api/v1", "risk_level": "Critical"},
            {"id": "api-open-weather", "name": "OpenWeather API", "provider": "OpenWeather", "endpoint": "https://api.openweathermap.org/data/2.5", "risk_level": "Low"},
            {"id": "api-wikipedia", "name": "Wikipedia API", "provider": "Wikipedia", "endpoint": "https://en.wikipedia.org/w/api.php", "risk_level": "Low"},
            {"id": "api-google-search", "name": "Google Search API", "provider": "Google", "endpoint": "https://www.googleapis.com/customsearch/v1", "risk_level": "Low"},
            {"id": "api-plaid-finance", "name": "Plaid Financial API", "provider": "Plaid", "endpoint": "https://api.plaid.com/v2", "risk_level": "High"},
            {"id": "api-hubspot-marketing", "name": "HubSpot Marketing API", "provider": "HubSpot", "endpoint": "https://api.hubapi.com/v1", "risk_level": "Low"},
            {"id": "api-notion-pages", "name": "Notion Workspace API", "provider": "Notion", "endpoint": "https://api.notion.com/v1", "risk_level": "Medium"},
            {"id": "api-zoom-meetings", "name": "Zoom Meeting Creator", "provider": "Zoom", "endpoint": "https://api.zoom.us/v2", "risk_level": "Low"},
            {"id": "api-figma-designs", "name": "Figma Files API", "provider": "Figma", "endpoint": "https://api.figma.com/v1", "risk_level": "Low"},
            {"id": "api-amplitude-analytics", "name": "Amplitude Tracking API", "provider": "Amplitude", "endpoint": "https://api.amplitude.com", "risk_level": "Medium"}
        ]
        
        for api in apis:
            session.run(
                "CREATE (api:API {id: $id, name: $name, provider: $provider, endpoint: $endpoint, risk_level: $risk_level})",
                **api
            )
            
        # 4. Create DataSources (25 nodes)
        datasources = [
            {"id": "db-production-mysql", "name": "Production Customer DB", "category": "Database", "sensitivity": "Confidential", "description": "Primary transactional database containing support logs and customer records."},
            {"id": "db-customer-crm", "name": "Salesforce CRM Database", "category": "Database", "sensitivity": "Confidential", "description": "Hubspot and Salesforce CRM details representing leads and deals."},
            {"id": "db-payroll-postgres", "name": "Production Payroll Database", "category": "Database", "sensitivity": "Highly Sensitive", "description": "PostgreSQL database containing employee salaries, routing numbers, and payouts."},
            {"id": "db-hr-workday", "name": "HR Workday Employee DB", "category": "Database", "sensitivity": "Confidential", "description": "Company directory containing PII: employee home addresses, social numbers, and phone records."},
            {"id": "s3-raw-invoice-files", "name": "Billing Invoices S3 Bucket", "category": "SaaS Storage", "sensitivity": "Restricted", "description": "Amazon S3 bucket containing raw invoice PDF files and customer transaction slips."},
            {"id": "s3-backup-storage", "name": "Production Backups S3 Bucket", "category": "SaaS Storage", "sensitivity": "Highly Sensitive", "description": "Production database database dumps and virtual machine backup snapshots."},
            {"id": "db-snowflake", "name": "Snowflake Data Warehouse", "category": "Database", "sensitivity": "Restricted", "description": "Enterprise-wide raw data warehouse containing aggregated business metrics."},
            {"id": "db-candidate-resumes", "name": "Candidate Resumes S3 Bucket", "category": "SaaS Storage", "sensitivity": "Internal", "description": "S3 bucket storing resumes of candidates applying for roles."},
            {"id": "db-zendesk-tickets", "name": "Zendesk Support Tickets DB", "category": "Database", "sensitivity": "Confidential", "description": "Archive of Zendesk support chats and support emails."},
            {"id": "db-elastic-logs", "name": "Elasticsearch System Logs", "category": "File System", "sensitivity": "Internal", "description": "Server diagnostics, system error details and api access records."},
            {"id": "kb-confluence", "name": "Confluence Internal Wiki", "category": "SaaS Storage", "sensitivity": "Internal", "description": "Internal product documentations, design patterns and general workflows."},
            {"id": "vault-passwords", "name": "Hashicorp Vault KV Store", "category": "Credentials", "sensitivity": "Highly Sensitive", "description": "Production database master secrets, api credentials, and TLS certificates."},
            {"id": "k8s-cluster-configs", "name": "Kubernetes Cluster Config Store", "category": "File System", "sensitivity": "Restricted", "description": "Deployment YAML config files, config maps, and container setups."},
            {"id": "db-marketing-leads", "name": "Marketing Campaign Leads DB", "category": "Database", "sensitivity": "Internal", "description": "Public newsletter signups and advertisement traffic log data."},
            {"id": "db-social-schedule", "name": "Buffer Social Media Schedule", "category": "Database", "sensitivity": "Internal", "description": "Queue containing draft tweets and schedules."},
            {"id": "gdrive-legal-contracts", "name": "Legal Contracts Google Drive", "category": "SaaS Storage", "sensitivity": "Restricted", "description": "Folder storing vendor NDAs, customer terms of service, and hiring agreements."},
            {"id": "db-inventory-catalog", "name": "Product Inventory Database", "category": "Database", "sensitivity": "Internal", "description": "Catalog of active stock levels, SKU IDs and price tables."},
            {"id": "db-public-kb", "name": "Public Help Articles DB", "category": "Database", "sensitivity": "Public", "description": "Standard documentation articles accessible by anyone."},
            {"id": "s3-github-repos", "name": "GitHub Repo Source Code", "category": "SaaS Storage", "sensitivity": "Restricted", "description": "Enterprise source code repositories."},
            {"id": "db-active-sessions", "name": "Redis Session Cache", "category": "Database", "sensitivity": "Confidential", "description": "Active user web sessions and authentication tokens."},
            {"id": "db-weather-cache", "name": "Weather Cache SQLite", "category": "Database", "sensitivity": "Public", "description": "Local cache database for weather endpoints."},
            {"id": "db-wiki-cache", "name": "Wikipedia Page Cache", "category": "Database", "sensitivity": "Public", "description": "SQLite file containing cached search pages."},
            {"id": "db-notion-wiki", "name": "Internal Knowledge Base DB", "category": "Database", "sensitivity": "Internal", "description": "Internal Notion database containing corporate wiki notes."},
            {"id": "db-plaid-sync", "name": "Plaid Bank Transactions DB", "category": "Database", "sensitivity": "Restricted", "description": "Local mirror of bank transaction history for invoice reconciliation."},
            {"id": "db-zoom-recordings", "name": "Zoom Meeting Video Storage", "category": "SaaS Storage", "sensitivity": "Restricted", "description": "Archive of recording audio and video from corporate Zoom calls."}
        ]
        
        for ds in datasources:
            session.run(
                "CREATE (d:DataSource {id: $id, name: $name, category: $category, sensitivity: $sensitivity, description: $description})",
                **ds
            )
            
        # 5. Create Policies (10 nodes)
        policies = [
            {"id": "policy-support-isolation", "name": "Support Agent Isolation Policy", "description": "Customer support agents must not access restricted financial spreadsheets or core credentials.", "severity": "High", "forbidden_sensitivities": ["Highly Sensitive"], "forbidden_categories": ["Financial", "HR", "Credentials"]},
            {"id": "policy-public-chatbot", "name": "Public Chatbot Sandboxing Policy", "description": "Public-facing chat bots are strictly prohibited from touching confidential, restricted, or highly sensitive databases.", "severity": "Critical", "forbidden_sensitivities": ["Confidential", "Restricted", "Highly Sensitive"], "forbidden_categories": ["Financial", "HR", "Credentials", "System Config"]},
            {"id": "policy-hr-isolation", "name": "HR Policy Access Boundary", "description": "HR assistants are allowed to view employee PII but must not have access to financial, invoicing or system configurations.", "severity": "High", "forbidden_sensitivities": ["Highly Sensitive"], "forbidden_categories": ["Financial", "Credentials"]},
            {"id": "policy-dev-shell-governance", "name": "Developer Agent Shell Restriction", "description": "Developer agents should not have connections to credentials database stores like Hashicorp Vault via active shell sessions.", "severity": "Critical", "forbidden_sensitivities": [], "forbidden_categories": ["Credentials"]},
            {"id": "policy-ops-governance", "name": "Operations Agent Policy", "description": "Operations agents should only access configuration files and system backups.", "severity": "Medium", "forbidden_sensitivities": [], "forbidden_categories": ["Financial", "HR"]},
            {"id": "policy-marketing-isolation", "name": "Marketing Tooling Boundary", "description": "Marketing agents should never touch client records, customer tickets or credentials.", "severity": "High", "forbidden_sensitivities": ["Confidential", "Restricted", "Highly Sensitive"], "forbidden_categories": ["Credentials", "HR", "Financial"]},
            {"id": "policy-sales-restriction", "name": "Sales Data Access Control", "description": "Sales outreach agents must only read customer lead directories.", "severity": "Medium", "forbidden_sensitivities": ["Highly Sensitive"], "forbidden_categories": ["Credentials", "HR"]},
            {"id": "policy-billing-pci", "name": "Billing PCI DSS Compliance", "description": "Billing agents should only access invoices and transaction records, not employee directory logs.", "severity": "Critical", "forbidden_sensitivities": [], "forbidden_categories": ["HR"]},
            {"id": "policy-chatbot-no-shell", "name": "Chatbot Command Execution Restriction", "description": "Directly prohibits customer-facing web chat agents from using server command line execution tools.", "severity": "Critical", "forbidden_sensitivities": [], "forbidden_categories": []},
            {"id": "policy-auditor-read-only", "name": "Compliance Auditor Access Policy", "description": "Auditors are prohibited from using tools that write or modify DataSources directly.", "severity": "High", "forbidden_sensitivities": [], "forbidden_categories": []}
        ]
        
        for p in policies:
            session.run(
                "CREATE (pol:Policy {id: $id, name: $name, description: $description, severity: $severity, forbidden_sensitivities: $forbidden_sensitivities, forbidden_categories: $forbidden_categories})",
                **p
            )
            
        # 6. Create Secrets (10 nodes)
        secrets = [
            {"id": "secret-support-slack", "name": "Slack Integration Bot Token", "type": "OAuth Token", "exposure_level": "Medium"},
            {"id": "secret-hr-workday", "name": "Workday Service Account Key", "type": "API Key", "exposure_level": "High"},
            {"id": "secret-stripe-live", "name": "Stripe Gateway Live Key", "type": "API Key", "exposure_level": "Critical"},
            {"id": "secret-prod-ssh-key", "name": "Production Server PEM SSH Key", "type": "SSH Key", "exposure_level": "Critical"},
            {"id": "secret-github-pat", "name": "GitHub Workspace PAT Token", "type": "OAuth Token", "exposure_level": "High"},
            {"id": "secret-sendgrid", "name": "SendGrid SMTP Auth Token", "type": "API Key", "exposure_level": "Medium"},
            {"id": "secret-aws-key", "name": "AWS IAM ReadOnly Credentials", "type": "API Key", "exposure_level": "High"},
            {"id": "secret-vault-token", "name": "Hashicorp Vault Production Root Token", "type": "API Key", "exposure_level": "Critical"},
            {"id": "secret-salesforce-oauth", "name": "Salesforce Integration Client Secret", "type": "OAuth Token", "exposure_level": "Medium"},
            {"id": "secret-twitter-oauth", "name": "Twitter API OAuth Credentials", "type": "OAuth Token", "exposure_level": "Low"}
        ]
        
        for s in secrets:
            session.run(
                "CREATE (sec:Secret {id: $id, name: $name, type: $type, exposure_level: $exposure_level})",
                **s
            )
            
        # 7. Create Permissions (10 nodes)
        # Permissions link Agents to DataSources directly. We also map ALLOWS relationships between Permissions and DataSources.
        permissions = [
            {"id": "perm-support-read-kb", "name": "Read Support KB Articles", "scope": "read"},
            {"id": "perm-support-read-tickets", "name": "Read Customer Support Tickets", "scope": "read"},
            {"id": "perm-hr-read-directory", "name": "Read Workday Employee Records", "scope": "read"},
            {"id": "perm-hr-write-directory", "name": "Write Workday Employee Records", "scope": "write"},
            {"id": "perm-dev-read-code", "name": "Read Code Repositories", "scope": "read"},
            {"id": "perm-dev-write-code", "name": "Write Code Repositories", "scope": "write"},
            {"id": "perm-finance-billing", "name": "Read Billing Invoice Data", "scope": "read"},
            {"id": "perm-ops-backup-admin", "name": "Write Database Backup Archives", "scope": "admin"},
            {"id": "perm-analytics-query-warehouse", "name": "Read Snowflake Business Metrics", "scope": "read"},
            {"id": "perm-chatbot-read-public", "name": "Read Public Support Articles", "scope": "read"}
        ]
        
        for perm in permissions:
            session.run(
                "CREATE (p:Permission {id: $id, name: $name, scope: $scope})",
                **perm
            )

        print("Nodes created. Establishing relationships...")
        
        # 8. Create relationships: USES (Agent -> Tool)
        uses_relations = [
            # Support Agent
            ("agent-support", "tool-crm-read"),
            ("agent-support", "tool-email-sender"),
            ("agent-support", "tool-slack-notifier"),
            ("agent-support", "tool-translator"),
            ("agent-support", "tool-wiki-reader"),
            ("agent-support", "tool-db-reader"), # HIGH RISK! Support agent shouldn't have raw DB query capability.
            
            # HR Assistant
            ("agent-hr", "tool-hr-portal"),
            ("agent-hr", "tool-email-sender"),
            ("agent-hr", "tool-resume-parser"),
            
            # Finance Agent
            ("agent-finance", "tool-payroll-calculator"),
            ("agent-finance", "tool-stripe-client"),
            
            # Sales Agent
            ("agent-sales", "tool-crm-read"),
            ("agent-sales", "tool-crm-write"),
            ("agent-sales", "tool-email-sender"),
            
            # Operations Agent
            ("agent-ops", "tool-backup-runner"),
            ("agent-ops", "tool-shell-executor"), # High Risk tool
            ("agent-ops", "tool-config-editor"),
            
            # Dev Agent
            ("agent-dev", "tool-github-client"),
            ("agent-dev", "tool-jira-integrator"),
            ("agent-dev", "tool-ssh-client"), # SSH access!
            
            # Analytics Agent
            ("agent-analytics", "tool-analytics-reporter"),
            
            # Billing Agent
            ("agent-billing", "tool-stripe-client"),
            ("agent-billing", "tool-email-sender"),
            
            # Public Website Chatbot
            ("agent-chatbot", "tool-web-search"),
            ("agent-chatbot", "tool-weather-api"),
            ("agent-chatbot", "tool-translator"),
            ("agent-chatbot", "tool-wiki-reader"),
            ("agent-chatbot", "tool-shell-executor"), # CRITICAL POLICY VIOLATION! Public chatbot using shell executor.
            
            # Security Agent
            ("agent-security", "tool-log-viewer"),
            ("agent-security", "tool-secret-rotator"),
            
            # Inventory Agent
            ("agent-inventory", "tool-db-reader"),
            
            # Social Poster
            ("agent-social", "tool-social-manager"),
            
            # Legal Agent
            ("agent-legal", "tool-legal-scanner"),
            
            # Recruiting Agent
            ("agent-recruiting", "tool-resume-parser"),
            ("agent-recruiting", "tool-email-sender"),
            
            # Backup Agent
            ("agent-backup", "tool-backup-runner"),
            
            # IT Support Agent
            ("agent-it-help", "tool-it-ticket-creator"),
            ("agent-it-help", "tool-log-viewer"),
            
            # Audit Agent
            ("agent-audit", "tool-analytics-reporter")
        ]
        
        for agent_id, tool_id in uses_relations:
            session.run(
                "MATCH (a:Agent {id: $agent_id}), (t:Tool {id: $tool_id}) CREATE (a)-[:USES]->(t)",
                agent_id=agent_id, tool_id=tool_id
            )
            
        # 9. Create relationships: CALLS (Tool -> API)
        calls_relations = [
            ("tool-crm-read", "api-salesforce-crm"),
            ("tool-crm-write", "api-salesforce-crm"),
            ("tool-email-sender", "api-sendgrid"),
            ("tool-slack-notifier", "api-slack-chat"),
            ("tool-payroll-calculator", "api-payroll"),
            
            # DB Reader calls many databases (simulated via DB APIs / raw access)
            ("tool-db-reader", "api-snowflake-warehouse"),
            ("tool-db-reader", "api-payroll"), # VIOLATION PATHWAY: Tool db-reader calls payroll API!
            
            ("tool-shell-executor", "api-ssh-shell"), # Shell executor executes via SSH API
            ("tool-file-manager", "api-aws-s3"),
            ("tool-web-search", "api-google-search"),
            ("tool-hr-portal", "api-hr-api"),
            ("tool-weather-api", "api-open-weather"),
            ("tool-stripe-client", "api-stripe-billing"),
            ("tool-jira-integrator", "api-jira-cloud"),
            ("tool-github-client", "api-github-rest"),
            ("tool-ssh-client", "api-ssh-shell"),
            ("tool-backup-runner", "api-backup-service"),
            ("tool-translator", "api-deepl-translator"),
            ("tool-analytics-reporter", "api-snowflake-warehouse"),
            ("tool-social-manager", "api-twitter-v2"),
            ("tool-legal-scanner", "api-google-drive"),
            ("tool-resume-parser", "api-greenhouse-ats"),
            ("tool-it-ticket-creator", "api-zendesk-support"),
            ("tool-log-viewer", "api-datadog-logs"),
            ("tool-wiki-reader", "api-confluence-kb"),
            ("tool-secret-rotator", "api-hashicorp-vault"),
            ("tool-config-editor", "api-kubernetes-control")
        ]
        
        for tool_id, api_id in calls_relations:
            session.run(
                "MATCH (t:Tool {id: $tool_id}), (api:API {id: $api_id}) CREATE (t)-[:CALLS]->(api)",
                tool_id=tool_id, api_id=api_id
            )
            
        # 10. Create relationships: ACCESSES (API -> DataSource)
        accesses_relations = [
            ("api-salesforce-crm", "db-customer-crm"),
            ("api-stripe-billing", "s3-raw-invoice-files"),
            ("api-stripe-billing", "db-plaid-sync"),
            ("api-hr-api", "db-hr-workday"),
            ("api-payroll", "db-payroll-postgres"),
            ("api-slack-chat", "db-zendesk-tickets"), # Slack channels index some customer details
            ("api-aws-s3", "s3-backup-storage"),
            ("api-github-rest", "s3-github-repos"),
            
            # SSH Shell API gives remote access to secrets vault and cluster configuration
            ("api-ssh-shell", "vault-passwords"), # HIGH RISK! SSH shell API reaches Vault!
            ("api-ssh-shell", "k8s-cluster-configs"),
            
            ("api-backup-service", "s3-backup-storage"),
            ("api-snowflake-warehouse", "db-snowflake"),
            ("api-twitter-v2", "db-social-schedule"),
            ("api-google-drive", "gdrive-legal-contracts"),
            ("api-google-drive", "db-candidate-resumes"),
            ("api-greenhouse-ats", "db-candidate-resumes"),
            ("api-zendesk-support", "db-zendesk-tickets"),
            ("api-datadog-logs", "db-elastic-logs"),
            ("api-confluence-kb", "kb-confluence"),
            ("api-hashicorp-vault", "vault-passwords"),
            ("api-kubernetes-control", "k8s-cluster-configs"),
            ("api-open-weather", "db-weather-cache"),
            ("api-wikipedia", "db-wiki-cache"),
            ("api-google-search", "db-wiki-cache"),
            ("api-plaid-finance", "db-plaid-sync"),
            ("api-hubspot-marketing", "db-marketing-leads"),
            ("api-notion-pages", "db-notion-wiki"),
            ("api-zoom-meetings", "db-zoom-recordings"),
            ("api-figma-designs", "kb-confluence"),
            ("api-amplitude-analytics", "db-snowflake")
        ]
        
        for api_id, ds_id in accesses_relations:
            session.run(
                "MATCH (api:API {id: $api_id}), (d:DataSource {id: $ds_id}) CREATE (api)-[:ACCESSES]->(d)",
                api_id=api_id, ds_id=ds_id
            )
            
        # 11. Create relationships: GOVERNED_BY (Agent -> Policy)
        governed_relations = [
            ("agent-support", "policy-support-isolation"),
            ("agent-chatbot", "policy-public-chatbot"),
            ("agent-chatbot", "policy-chatbot-no-shell"),
            ("agent-hr", "policy-hr-isolation"),
            ("agent-dev", "policy-dev-shell-governance"),
            ("agent-ops", "policy-ops-governance"),
            ("agent-marketing", "policy-marketing-isolation"),
            ("agent-sales", "policy-sales-restriction"),
            ("agent-billing", "policy-billing-pci"),
            ("agent-social", "policy-marketing-isolation"),
            ("agent-recruiting", "policy-hr-isolation"),
            ("agent-audit", "policy-auditor-read-only")
        ]
        
        for agent_id, policy_id in governed_relations:
            session.run(
                "MATCH (a:Agent {id: $agent_id}), (p:Policy {id: $policy_id}) CREATE (a)-[:GOVERNED_BY]->(p)",
                agent_id=agent_id, policy_id=policy_id
            )
            
        # 12. Create relationships: HAS_SECRET (Agent -> Secret)
        has_secret_relations = [
            ("agent-support", "secret-support-slack"),
            ("agent-support", "secret-sendgrid"),
            ("agent-hr", "secret-hr-workday"),
            ("agent-finance", "secret-stripe-live"),
            ("agent-dev", "secret-github-pat"),
            ("agent-dev", "secret-prod-ssh-key"), # Dev agent holding production server key! High risk.
            ("agent-ops", "secret-aws-key"),
            ("agent-security", "secret-vault-token"),
            ("agent-sales", "secret-salesforce-oauth"),
            ("agent-social", "secret-twitter-oauth"),
            ("agent-billing", "secret-stripe-live")
        ]
        
        for agent_id, secret_id in has_secret_relations:
            session.run(
                "MATCH (a:Agent {id: $agent_id}), (s:Secret {id: $secret_id}) CREATE (a)-[:HAS_SECRET]->(s)",
                agent_id=agent_id, secret_id=secret_id
            )
            
        # 13. Create relationships: HAS_PERMISSION (Agent -> Permission)
        agent_permissions = [
            ("agent-support", "perm-support-read-kb"),
            ("agent-support", "perm-support-read-tickets"),
            ("agent-hr", "perm-hr-read-directory"),
            ("agent-hr", "perm-hr-write-directory"),
            ("agent-dev", "perm-dev-read-code"),
            ("agent-dev", "perm-dev-write-code"),
            ("agent-finance", "perm-finance-billing"),
            ("agent-ops", "perm-ops-backup-admin"),
            ("agent-analytics", "perm-analytics-query-warehouse"),
            ("agent-chatbot", "perm-chatbot-read-public"),
            ("agent-recruiting", "perm-hr-read-directory")
        ]
        
        for agent_id, perm_id in agent_permissions:
            session.run(
                "MATCH (a:Agent {id: $agent_id}), (p:Permission {id: $perm_id}) CREATE (a)-[:HAS_PERMISSION]->(p)",
                agent_id=agent_id, perm_id=perm_id
            )
            
        # 14. Create relationships: ALLOWS (Permission -> DataSource)
        permission_allows = [
            ("perm-support-read-kb", "db-public-kb"),
            ("perm-support-read-tickets", "db-zendesk-tickets"),
            ("perm-hr-read-directory", "db-hr-workday"),
            ("perm-hr-write-directory", "db-hr-workday"),
            ("perm-dev-read-code", "s3-github-repos"),
            ("perm-dev-write-code", "s3-github-repos"),
            ("perm-finance-billing", "s3-raw-invoice-files"),
            ("perm-ops-backup-admin", "s3-backup-storage"),
            ("perm-analytics-query-warehouse", "db-snowflake"),
            ("perm-chatbot-read-public", "db-public-kb")
        ]
        
        for perm_id, ds_id in permission_allows:
            session.run(
                "MATCH (p:Permission {id: $perm_id}), (d:DataSource {id: $ds_id}) CREATE (p)-[:ALLOWS]->(d)",
                perm_id=perm_id, ds_id=ds_id
            )
            
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    verify_ok, msg = verify_connection()
    if not verify_ok:
        print(f"Could not connect to database: {msg}")
        sys.exit(1)
    seed_database()
    close_driver()
