import json
import faiss
import numpy as np

# Load text snippets
with open('text_snippets.json', 'r', encoding='utf-8') as f:
    text_snippets = json.load(f)

# Load FAISS index
faiss_index = faiss.read_index('faiss_index.bin')

# Load embeddings
embeddings = np.load('embeddings.npy')

print(f"Number of text snippets: {len(text_snippets)}")
print(f"FAISS index size: {faiss_index.ntotal}")
print(f"Number of embeddings: {len(embeddings)}")

# Check if indices in text_snippets match FAISS index
max_index = max(int(idx) for idx in text_snippets.keys())
print(f"Maximum index in text_snippets: {max_index}")

# Print a few sample entries from text_snippets
print("\nSample entries from text_snippets:")
for i, (idx, text) in enumerate(list(text_snippets.items())[:5]):
    print(f"{idx}: {text[:50]}...")

# Print dimensions of embeddings
print(f"\nEmbeddings shape: {embeddings.shape}")

# Check FAISS index type
print(f"FAISS index type: {type(faiss_index)}")
