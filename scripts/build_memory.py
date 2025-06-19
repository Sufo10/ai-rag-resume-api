import os
import sys
from pathlib import Path
from config import EnvConfig

# Ensure we're running from the project root
if __name__ == "__main__":
    # Get the project root directory
    project_root = Path(__file__).resolve().parent.parent

    # Change to the project root directory
    os.chdir(str(project_root))

    # Add the project root to the Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from utils.retriever import create_faiss_index


def split_text(text, max_tokens=200):
    words = text.split()
    chunks = [' '.join(words[i:i+max_tokens])
              for i in range(0, len(words), max_tokens)]
    return chunks


def build_memory(label):
    data_path = f"{EnvConfig.DATA_DIR}/{label}.md"
    with open(data_path, "r") as f:
        text = f.read()

    chunks = split_text(text)
    print(f"📄 {label}: {len(chunks)} chunks")

    os.makedirs(f"{EnvConfig.VECTOR_STORE_DIR}", exist_ok=True)
    index_path = f"{EnvConfig.VECTOR_STORE_DIR}/{label}.index"
    mapping_path = f"{EnvConfig.VECTOR_STORE_DIR}/{label}.json"

    create_faiss_index(chunks, index_path, mapping_path)
    print(f"✅ Memory built for {label}:")
    print(f"   ➤ {index_path}")
    print(f"   ➤ {mapping_path}")


if __name__ == "__main__":
    labels = [
        "profile",
        "experience",
        "education",
        "technologies",
        "projects",
        "certifications",
    ]

    for label in labels:
        build_memory(label)
