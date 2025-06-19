from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize the model globally for reuse
_model = None


def get_embedding(text: str, model_name="all-MiniLM-L6-v2"):
    """Get embeddings for a text using sentence-transformers.

    Args:
        text (str): The text to embed
        model_name (str): The model to use for embeddings. Defaults to 'all-MiniLM-L6-v2'
            which is a good balance of speed and quality.

    Returns:
        list: The embedding vector as a list of floats
    """
    global _model

    if _model is None:
        _model = SentenceTransformer(model_name)

    # Convert text to embedding
    embedding = _model.encode(text, convert_to_numpy=True)

    # Convert to list and return
    return embedding.tolist()
