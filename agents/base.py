from utils.retriever import query_faiss
from utils.llm_groq import ask_llm
from typing import List


class BaseAgent:
    def __init__(self, index_name: str):
        """
        Initialize an agent for a specific type of information

        Args:
            index_name (str): Name of the index (e.g., "experience", "projects")
        """
        self.index_name = index_name

    def get_response(self, question: str) -> str:
        """
        Get a response based on the question and relevant context

        Args:
            question (str): The user's question

        Returns:
            str: Generated response based on context
        """
        chunks = query_faiss(
            question,
            f"vector_store/{self.index_name}.index",
            f"vector_store/{self.index_name}.json"
        )

        if not chunks:
            return f"Sorry, I couldn't find relevant information about {self.index_name}."

        # Create a prompt that ensures the response is based only on the provided context
        prompt = f"""Based only on the following context about {self.index_name}, please answer the question.
        If you cannot find the information in the context, say that you don't have that information.
        
        Context:
        {chunks}
        
        Question: {question}
        """

        return ask_llm(prompt, question)
