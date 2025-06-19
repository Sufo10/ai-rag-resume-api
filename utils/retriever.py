# utils/retriever.py

import faiss
import numpy as np
import json
from utils.embedder import get_embedding


def create_faiss_index(doc_chunks, index_path, mapping_path):
    # Embed a sample to get the dimensionality
    dimension = len(get_embedding("hello world"))
    index = faiss.IndexFlatL2(dimension)

    vectors = []
    mapping = []

    for chunk in doc_chunks:
        embedding = get_embedding(chunk)
        vectors.append(embedding)
        mapping.append(chunk)

    index.add(np.array(vectors).astype("float32"))
    faiss.write_index(index, index_path)

    with open(mapping_path, "w") as f:
        json.dump(mapping, f)


def query_faiss(query: str, index_path: str, mapping_path: str, k: int = 3):
    """
    Query the FAISS index to find relevant context

    Args:
        query (str): The question to find context for
        index_path (str): Path to the FAISS index file
        mapping_path (str): Path to the JSON mapping file
        k (int): Number of results to return

    Returns:
        list: List of relevant text chunks
    """
    # Load the index
    index = faiss.read_index(index_path)

    # Load the mapping
    with open(mapping_path, "r") as f:
        mapping = json.load(f)

    # Get query embedding
    query_vector = np.array([get_embedding(query)]).astype("float32")

    # Search
    D, I = index.search(query_vector, k)

    # Filter out any negative indices and get the corresponding chunks
    return [mapping[int(i)] for i in I[0] if i >= 0]
