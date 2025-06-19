# agents/project_agent.py
from utils.retriever import query_faiss
from utils.llm_groq import ask_groq


def project_agent(question: str):
    chunks = query_faiss(
        question,
        "vector_store/project.index",
        "vector_store/project.json"
    )
    if not chunks:
        return "Sorry, nothing relevant found in your project context."

    context = "\n".join(chunks)
    return ask_groq(context, question)
