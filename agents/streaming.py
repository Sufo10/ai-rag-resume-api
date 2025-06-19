from typing import Generator, Any
from utils.retriever import query_faiss
from utils.llm_stream import stream_llm


class StreamingAgent:
    def __init__(self, index_name: str):
        """
        Initialize a streaming agent for a specific type of information

        Args:
            index_name (str): Name of the index (e.g., "experience", "projects")
        """
        self.index_name = index_name

    def get_streaming_response(self, question: str) -> Generator[str, Any, None]:
        """
        Get a streaming response based on the question and relevant context

        Args:
            question (str): The user's question

        Yields:
            str: Generated response chunks based on context
        """
        chunks = query_faiss(
            question,
            f"vector_store/{self.index_name}.index",
            f"vector_store/{self.index_name}.json"
        )

        if not chunks:
            yield f"Sorry, I couldn't find relevant information about {self.index_name}."
            return

        # Create a prompt that ensures the response is based only on the provided context
        prompt = f"""Based only on the following context about {self.index_name}, please answer the question.
        If you cannot find the information in the context, say that you don't have that information.
        
        Context:
        {chunks}
        
        Question: {question}
        """

        yield from stream_llm(prompt, question)


class StreamingProfileAgent(StreamingAgent):
    def __init__(self):
        super().__init__("profile")


class StreamingExperienceAgent(StreamingAgent):
    def __init__(self):
        super().__init__("experience")


class StreamingProjectsAgent(StreamingAgent):
    def __init__(self):
        super().__init__("projects")


class StreamingEducationAgent(StreamingAgent):
    def __init__(self):
        super().__init__("education")


class StreamingTechnologiesAgent(StreamingAgent):
    def __init__(self):
        super().__init__("technologies")


class StreamingCertificationsAgent(StreamingAgent):
    def __init__(self):
        super().__init__("certifications")
