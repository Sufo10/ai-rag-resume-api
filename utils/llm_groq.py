# utils/llm_groq.py
import requests
import json
from typing import Dict, Any
from config import EnvConfig


def validate_llm_response(response: requests.Response, provider: str) -> str:
    """Validate and extract content from LLM API response"""
    try:
        if not response.ok:
            response_json = response.json()
            error_msg = response_json.get(
                'error', {}).get('message', response.text)
            return f"{provider} API Error: {error_msg}"

        response_json = response.json()

        if not isinstance(response_json, dict):
            return f"{provider} Error: Invalid response format"

        choices = response_json.get('choices', [])
        if not choices or not isinstance(choices, list):
            return f"{provider} Error: No valid choices in response"

        message = choices[0].get('message', {})
        if not isinstance(message, dict):
            return f"{provider} Error: Invalid message format"

        content = message.get('content')
        if not content or not isinstance(content, str):
            return f"{provider} Error: No valid content in response"

        return content.strip()

    except json.JSONDecodeError:
        return f"{provider} Error: Invalid JSON response"
    except Exception as e:
        return f"{provider} Error: {str(e)}"


def ask_openai(context: str, question: str) -> str:
    headers = {
        "Authorization": f"Bearer {EnvConfig.OPENAI_API_KEY}",
        "Content-Type": "application/json"
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
            }
        )
        return validate_llm_response(response, "OpenAI")
    except requests.RequestException as e:
        return f"OpenAI Request Error: {str(e)}"
    except Exception as e:
        return f"OpenAI Error: {str(e)}"


def ask_groq(context: str, question: str) -> str:
    headers = {
        "Authorization": f"Bearer {EnvConfig.GROQ_API_KEY}",
        "Content-Type": "application/json"
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
            }
        )
        return validate_llm_response(response, "Groq")
    except requests.RequestException as e:
        return f"Groq Request Error: {str(e)}"
    except Exception as e:
        return f"Groq Error: {str(e)}"


def ask_llm(context: str, question: str) -> str:
    """
    Generic function to ask questions to the configured LLM provider
    """
    if EnvConfig.LLM_PROVIDER.lower() == "groq":
        if not EnvConfig.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured")
        return ask_groq(context, question)
    else:  # default to OpenAI
        if not EnvConfig.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")
        return ask_openai(context, question)
