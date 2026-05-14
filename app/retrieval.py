import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

with open("data/shl_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

documents = [
    item["name"] + " " + item["description"]
    for item in catalog
]

vectorizer = TfidfVectorizer(
    stop_words="english"
)

doc_vectors = vectorizer.fit_transform(
    documents
)


def search_assessments(query, top_k=5):

    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(
        query_vector,
        doc_vectors
    ).flatten()

    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []

    for idx in top_indices:

        item = catalog[idx]

        results.append({
            "name": item["name"],
            "url": item["url"],
            "description": item["description"]
        })

    return results
