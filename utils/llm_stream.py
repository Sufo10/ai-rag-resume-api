import requests
import json
from typing import Generator, Any
from config import EnvConfig


def stream_openai(context: str, question: str) -> Generator[str, Any, None]:
    headers = {
        "Authorization": f"Bearer {EnvConfig.OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    prompt = f"""You are a helpful assistant. You must only answer using the context below.

Context:
{context}

Question:
{question}

Important: Base your response ONLY on the provided context. If you cannot find the information in the context, say so."""

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": EnvConfig.OPENAI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "stream": True,
            },
            stream=True
        )

        if response.status_code != 200:
            yield f"OpenAI API Error: {response.text}"
            return

        for line in response.iter_lines():
            if line:
                try:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        if line_text.strip() == 'data: [DONE]':
                            break
                        json_str = line_text[6:]  # Remove 'data: '
                        json_obj = json.loads(json_str)
                        content = json_obj.get('choices', [{}])[0].get(
                            'delta', {}).get('content', '')
                        if content:
                            yield content
                except Exception as e:
                    yield f"Error parsing stream: {str(e)}"
                    break

    except Exception as e:
        yield f"OpenAI Streaming Error: {str(e)}"


def stream_groq(context: str, question: str) -> Generator[str, Any, None]:
    headers = {
        "Authorization": f"Bearer {EnvConfig.GROQ_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    prompt = f"""You are a helpful assistant. You must only answer using the context below.

Context:
{context}

Question:
{question}

Important: Base your response ONLY on the provided context. If you cannot find the information in the context, say so."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json={
                "model": EnvConfig.GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "stream": True,
            },
            stream=True
        )

        if response.status_code != 200:
            yield f"Groq API Error: {response.text}"
            return

        for line in response.iter_lines():
            if line:
                try:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        if line_text.strip() == 'data: [DONE]':
                            break
                        json_str = line_text[6:]  # Remove 'data: '
                        json_obj = json.loads(json_str)
                        content = json_obj.get('choices', [{}])[0].get(
                            'delta', {}).get('content', '')
                        if content:
                            yield content
                except Exception as e:
                    yield f"Error parsing stream: {str(e)}"
                    break

    except Exception as e:
        yield f"Groq Streaming Error: {str(e)}"


def stream_llm(context: str, question: str) -> Generator[str, Any, None]:
    """
    Generic function to stream responses from the configured LLM provider
    """
    if EnvConfig.LLM_PROVIDER.lower() == "groq":
        if not EnvConfig.GROQ_API_KEY:
            yield "Error: GROQ_API_KEY is not configured"
            return
        yield from stream_groq(context, question)
    else:  # default to OpenAI
        if not EnvConfig.OPENAI_API_KEY:
            yield "Error: OPENAI_API_KEY is not configured"
            return
        yield from stream_openai(context, question)
