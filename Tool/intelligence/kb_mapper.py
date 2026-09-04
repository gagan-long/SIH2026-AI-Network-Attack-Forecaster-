# intelligence/kb_mapper.py

# A Knowledge Graph mapping MITRE Tactics to known vulnerabilities and attack patterns.
MITRE_KNOWLEDGE_BASE = {
    "Reconnaissance": {
        "description": "The adversary is trying to gather information they can use to plan future operations.",
        "capec_ids": ["CAPEC-112 (Brute Force)", "CAPEC-285 (Port Scanning)"],
        "mitigation": "Restrict inbound traffic to essential ports. Implement rate limiting."
    },
    "Initial Access": {
        "description": "The adversary is trying to get into your network.",
        "capec_ids": ["CAPEC-66 (SQL Injection)", "CAPEC-18 (Exploiting Incorrectly Configured Access Control)"],
        "cves": ["CVE-2021-44228 (Log4Shell)", "CVE-2023-23397 (Outlook EoP)"],
        "mitigation": "Enforce MFA, patch public-facing applications, and monitor authentication logs."
    },
    "Lateral Movement": {
        "description": "The adversary is trying to move through your environment.",
        "capec_ids": ["CAPEC-540 (Overpass the Hash)", "CAPEC-309 (Exploitation of Privilege/Trust)"],
        "mitigation": "Implement network segmentation, disable SMBv1, and use LAPS for local admin passwords."
    },
    "C2": {
        "description": "The adversary is trying to communicate with compromised systems to control them.",
        "capec_ids": ["CAPEC-673 (Command and Control)"],
        "mitigation": "Block known malicious IPs via threat feeds and analyze outbound DNS for DGA domains."
    },
    "Exfiltration": {
        "description": "The adversary is trying to steal data.",
        "capec_ids": ["CAPEC-602 (Data Obfuscation)"],
        "mitigation": "Implement Data Loss Prevention (DLP) and monitor for abnormal outbound data volumes."
    },
    "Impact": {
        "description": "The adversary is trying to manipulate, interrupt, or destroy your systems and data.",
        "capec_ids": ["CAPEC-125 (Flooding)", "CAPEC-119 (Deplete Resources)"],
        "mitigation": "Implement anti-DDoS scrubbing services and maintain immutable offline backups."
    }
}

def get_threat_context(tactic_name):
    """Returns the threat intelligence context for a given MITRE tactic."""
    return MITRE_KNOWLEDGE_BASE.get(tactic_name, {
        "description": "Unknown or unmapped tactical behavior.",
        "capec_ids": [],
        "cves": [],
        "mitigation": "Investigate underlying flow characteristics manually."
    })