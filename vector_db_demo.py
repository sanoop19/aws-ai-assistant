from sentence_transformers import SentenceTransformer
import chromadb

# Initialize embedding model and ChromaDB
model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.Client()

# Create a collection (like a table in regular DB)
collection = chroma_client.create_collection("ba_security_demo")

# Sample Well-Architected Framework chunks
# (These are simplified versions of real framework text)
documents = [
    "SEC 7: Protect data in transit. Use TLS 1.2 or higher for all network communications. Implement HTTPS for all API endpoints.",
    "SEC 8: Protect data at rest. Use KMS encryption for all storage services including S3, RDS, and DynamoDB.",
    "REL 6: Implement redundancy. Deploy across multiple Availability Zones to prevent single points of failure.",
    "REL 9: Back up data. Implement automated backups with tested recovery procedures.",
    "COST 3: Select the right resource type. Use AWS Compute Optimizer to right-size Lambda and EC2 instances.",
    "SEC 2: Use IAM roles with least privilege. Apply permission boundaries to prevent privilege escalation.",
    "OPS 5: Enable logging and monitoring. Configure CloudWatch for all services and set up alerts.",
]

# Store documents with their embeddings
print("Storing documents in vector database...\n")

embeddings = model.encode(documents).tolist()

collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=[f"doc_{i}" for i in range(len(documents))]
)

print(f"✅ Stored {len(documents)} chunks in ChromaDB\n")
print("="*50)

# Now search with different queries
queries = [
    "Is our data encrypted when moving between services?",
    "What should we do about IAM permissions?",
    "How do we make sure the system doesn't go down?",
]

for query in queries:
    print(f"\n🔍 QUERY: '{query}'")
    
    # Convert query to embedding
    query_embedding = model.encode([query]).tolist()
    
    # Search ChromaDB for most similar chunks
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=2  # Return top 2 matches
    )
    
    print("📄 RETRIEVED CHUNKS:")
    for i, doc in enumerate(results['documents'][0]):
        print(f"  {i+1}. {doc}")