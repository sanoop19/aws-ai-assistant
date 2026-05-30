from pypdf import PdfReader
import re

def load_pdf(filepath):
    """Load PDF and extract text"""
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Don't cut mid-sentence - find nearest full stop
        if end < len(text):
            last_period = text.rfind('.', start, end)
            if last_period > start:
                end = last_period + 1
        
        chunk = text[start:end].strip()
        
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move forward with overlap
        start = end - overlap
    
    return chunks

# Test with a small sample text first
sample_text = """
SEC 7: Protect Data in Transit. 
All data transmitted between services must use TLS 1.2 or higher. 
HTTPS must be enforced on all public endpoints. 
Certificate management should use AWS Certificate Manager.
Internal service communication within VPCs should also be encrypted.

SEC 8: Protect Data at Rest.
Use AWS KMS for encryption key management across all storage services.
S3 buckets must have server-side encryption enabled.
RDS instances must have encryption at rest enabled at creation time.
DynamoDB tables should use AWS managed keys for encryption.

REL 6: Use Redundancy.
Deploy workloads across multiple Availability Zones.
Use Auto Scaling groups to maintain desired capacity.
Implement health checks on all load balancers.
Design for automatic failover without manual intervention.
"""

print("CHUNKING DEMO")
print("="*50)
print(f"Original text: {len(sample_text)} characters\n")

chunks = chunk_text(sample_text, chunk_size=300, overlap=50)

print(f"Number of chunks: {len(chunks)}\n")

for i, chunk in enumerate(chunks):
    print(f"CHUNK {i+1} ({len(chunk)} chars):")
    print(f"{chunk}")
    print("-"*30)