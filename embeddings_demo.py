from sentence_transformers import SentenceTransformer
import numpy as np

# Free model that runs locally on your machine
model = SentenceTransformer('all-MiniLM-L6-v2')

# Three sentences - two similar, one different
sentences = [
    "Encrypt all data in transit using TLS",
    "Use HTTPS for all API connections",
    "Book a flight from London to New York"
]

print("Converting sentences to embeddings...\n")

embeddings = model.encode(sentences)

for i, sentence in enumerate(sentences):
    print(f"'{sentence}'")
    print(f"Vector length: {len(embeddings[i])} numbers")
    print(f"First 5 numbers: {embeddings[i][:5]}\n")

# Measure similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("="*50)
print("SIMILARITY SCORES\n")

sim_1_2 = cosine_similarity(embeddings[0], embeddings[1])
sim_1_3 = cosine_similarity(embeddings[0], embeddings[2])
sim_2_3 = cosine_similarity(embeddings[1], embeddings[2])

print(f"'Encrypt TLS' vs 'Use HTTPS':    {sim_1_2:.3f} ← should be HIGH")
print(f"'Encrypt TLS' vs 'Book flight':  {sim_1_3:.3f} ← should be LOW")
print(f"'Use HTTPS'   vs 'Book flight':  {sim_2_3:.3f} ← should be LOW")