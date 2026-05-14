import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index("data/faiss.index")

with open("data/shl_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)


def search_assessments(query, top_k=10):
    emb = model.encode([query])

    distances, indices = index.search(
        np.array(emb, dtype=np.float32),
        top_k
    )

    results = []

    for idx in indices[0]:
        item = catalog[idx]

        results.append({
            "name": item["name"],
            "url": item["url"],
            "description": item["description"]
        })

    return results