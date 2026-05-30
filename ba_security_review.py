import streamlit as st
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="BA Security Review", page_icon="✈️")

# Initialize Anthropic client
client = anthropic.Anthropic()

# BA Security Rules - built from your knowledge
BA_SECURITY_RULES = """
You are a British Airways AWS Security Review Assistant.
You check new projects against BA's specific security standards.

BA SECURITY RULES:

RULE 1 — ENCRYPTION
- All data in transit MUST be encrypted (TLS)
- All data at rest MUST be encrypted
- FAIL if encryption not explicitly mentioned

RULE 2 — SECURITY GROUPS
- Inbound 0.0.0.0/0 is NEVER allowed
- Outbound open is acceptable
- FAIL if any inbound rule allows 0.0.0.0/0

RULE 3 — LOGGING
- CloudWatch logging is ALWAYS required
- S3 logging is MANDATORY if PCI or payment data
- S3 logging is project decision for non-PCI
- FAIL if CloudWatch logging not mentioned

RULE 4 — IAM
- Over-permissive roles are NOT allowed
- Permission boundaries are MANDATORY on all roles
- Admin access only via HUPA (28 day limit)
- All deployments must use GitHub OIDC + Terraform
- FAIL if permission boundaries not mentioned

RULE 5 — DATA CLASSIFICATION
- PII/Passenger data must be in encrypted RDS
- PCI/Payment data needs S3 logging + encryption
- FAIL if PCI data handling is unclear

RULE 6 — NETWORKING
- Public endpoints MUST have Akamai + WAF
- WAF must whitelist ONLY Akamai IPs
- External APIs (Amadeus etc) must go via Datacentre/MPLS
- FAIL if public endpoints exist without Akamai/WAF

RULE 7 — DOCUMENTATION
- Architecture diagram must clearly show all ports
- Encryption must be explicitly stated
- PCI data flow must be clearly documented
- FAIL if ports or encryption not documented

SCORING:
- PASSED: Requirement clearly met
- FAILED: Requirement clearly not met - must fix before Cyber review
- NEEDS CLARIFICATION: Not enough information provided

OUTPUT FORMAT:
Always respond in this exact format:

## ✈️ BA PRE-CYBER SECURITY REVIEW
**Project:** [project name]
**Data Classification:** [classification]
**Review Date:** [today's date]

---

## ✅ PASSED
[list each passed item]

## ❌ FAILED — FIX BEFORE CYBER REVIEW
[list each failed item with specific fix needed]

## ⚠️ NEEDS CLARIFICATION
[list items needing more info]

---

## 📋 READY FOR CYBER TEAM: YES/NO

**Summary:** [2-3 sentence summary]

**Next Steps:** [specific actions for project team]
"""

# App UI
st.title("✈️ BA Pre-Cyber Security Review")
st.markdown("*Complete this form before submitting to the Cyber Security team*")

st.divider()

# Project details form
col1, col2 = st.columns(2)

with col1:
    project_name = st.text_input("Project Name", placeholder="e.g. BA Payment Gateway v2")
    
with col2:
    data_classification = st.selectbox(
        "Data Classification",
        ["Internal", "PII - Passenger Data", "PCI - Payment Data", "Financial", "Public"]
    )

aws_services = st.multiselect(
    "AWS Services Used",
    ["Lambda", "ECS Fargate", "EC2", "RDS", "S3", "API Gateway", 
     "CloudFront", "WAF", "CloudWatch", "IAM", "VPC", "CloudWAN",
     "DynamoDB", "SQS", "SNS", "Secrets Manager", "KMS"]
)

architecture_description = st.text_area(
    "Architecture Description",
    placeholder="""Describe your architecture including:
- What the system does
- How data flows between services
- Security controls in place
- External connections (internet, Amadeus, on-prem)
- IAM approach
- Encryption details
- Ports used""",
    height=200
)

external_connections = st.multiselect(
    "External Connections",
    ["Internet (direct)", "Akamai/WAF", "Amadeus via MPLS", 
     "Datacentre via CloudWAN", "Third party APIs", "On-premise via Direct Connect"]
)

deployment_method = st.selectbox(
    "Deployment Method",
    ["GitHub OIDC + Terraform", "Manual", "Other CI/CD", "AWS Console"]
)

# Submit button
if st.button("🔍 Run Security Review", type="primary"):
    
    if not project_name or not architecture_description:
        st.error("Please fill in Project Name and Architecture Description")
    else:
        # Build the prompt
        user_prompt = f"""
Please review this British Airways project against BA security standards:

PROJECT NAME: {project_name}
DATA CLASSIFICATION: {data_classification}
AWS SERVICES: {', '.join(aws_services) if aws_services else 'Not specified'}
EXTERNAL CONNECTIONS: {', '.join(external_connections) if external_connections else 'None'}
DEPLOYMENT METHOD: {deployment_method}

ARCHITECTURE DESCRIPTION:
{architecture_description}

Please check against ALL BA security rules and provide the full review report.
"""
        
        with st.spinner("🔍 Reviewing against BA security standards..."):
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=BA_SECURITY_RULES,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            review_result = response.content[0].text
        
        st.divider()
        st.markdown(review_result)
        
        # Show token usage
        with st.expander("📊 API Usage"):
            st.write(f"Input tokens: {response.usage.input_tokens}")
            st.write(f"Output tokens: {response.usage.output_tokens}")