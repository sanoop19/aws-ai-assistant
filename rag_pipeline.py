from sentence_transformers import SentenceTransformer
import chromadb
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize everything
print("🚀 Initializing RAG Pipeline...\n")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.Client()
claude_client = anthropic.Anthropic()

# Create ChromaDB collection
collection = chroma_client.create_collection("well_architected")

# ─────────────────────────────────────────
# STEP 1: Our "documents" (Well-Architected chunks)
# Later we'll replace this with the real PDF
# ─────────────────────────────────────────
documents = [
    "SEC 7: Protect data in transit. Use TLS 1.2 or higher for all network communications. Implement HTTPS for all API endpoints and service-to-service communication.",
    "SEC 8: Protect data at rest. Use AWS KMS for encryption key management. Enable encryption on S3, RDS, and DynamoDB. Encryption at rest must be enabled at resource creation.",
    "SEC 2: Apply least privilege IAM. Use IAM roles with minimal permissions. Apply permission boundaries to all roles to prevent privilege escalation. Never use root account for operations.",
    "SEC 3: Manage secrets securely. Use AWS Secrets Manager or Parameter Store for credentials. Never hardcode secrets in code or environment variables.",
    "REL 6: Use redundancy. Deploy across multiple Availability Zones. Use Auto Scaling to maintain capacity. Design for automatic failover.",
    "REL 9: Back up data regularly. Implement automated backups. Test recovery procedures. Define RTO and RPO for all critical workloads.",
    "OPS 5: Enable observability. Configure CloudWatch logging for all services. Set up alerts for critical metrics. Enable VPC Flow Logs and CloudTrail.",
    "COST 3: Right-size resources. Use AWS Compute Optimizer for recommendations. Monitor Lambda memory usage. Use Savings Plans for predictable workloads.",
    "SEC 6: Protect network layers. Use WAF for public endpoints. Restrict security group inbound rules. Never allow 0.0.0.0/0 inbound. Use private subnets for sensitive workloads.",
    "PER 4: Monitor performance. Use CloudWatch metrics and X-Ray tracing. Set up performance baselines. Configure auto-scaling based on demand.",
]

# ─────────────────────────────────────────
# STEP 2: Store documents in ChromaDB
# ─────────────────────────────────────────
print("📄 Loading documents into vector database...")
embeddings = embedding_model.encode(documents).tolist()
collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=[f"doc_{i}" for i in range(len(documents))]
)
print(f"✅ Stored {len(documents)} chunks\n")

# ─────────────────────────────────────────
# STEP 3: RAG Query Function
# ─────────────────────────────────────────
def rag_query(question, n_chunks=3):
    """
    Full RAG pipeline:
    1. Convert question to embedding
    2. Find similar chunks in ChromaDB
    3. Send chunks + question to Claude
    4. Return answer grounded in framework
    """
    
    # Retrieve relevant chunks
    query_embedding = embedding_model.encode([question]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_chunks
    )
    
    retrieved_chunks = results['documents'][0]
    
    # Build context from retrieved chunks
    context = "\n\n".join([f"- {chunk}" for chunk in retrieved_chunks])
    
    # Send to Claude with retrieved context
    prompt = f"""You are an AWS Well-Architected Framework expert.

Answer the question using ONLY the provided framework excerpts below.
Be specific and cite which pillar/section your answer comes from.

FRAMEWORK EXCERPTS:
{context}

QUESTION: {question}
"""
    
    response = claude_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text, retrieved_chunks

# ─────────────────────────────────────────
# STEP 4: Test it
# ─────────────────────────────────────────
questions = [
    "How should we handle encryption for our RDS database storing passenger data?",
    "Our Lambda functions have admin IAM roles - is this acceptable?",
    "We have a public API Gateway with no WAF - what are the risks?",
]

print("="*60)
print("🔍 TESTING RAG PIPELINE")
print("="*60)

for question in questions:
    print(f"\n❓ QUESTION: {question}")
    print("\n📄 RETRIEVED CHUNKS:")
    
    answer, chunks = rag_query(question)
    
    for i, chunk in enumerate(chunks):
        print(f"  {i+1}. {chunk[:80]}...")
    
    print(f"\n🤖 CLAUDE'S ANSWER:")
    print(answer)
    print("\n" + "="*60)