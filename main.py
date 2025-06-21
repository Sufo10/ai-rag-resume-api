from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os
from fastapi.responses import StreamingResponse, JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from config import EnvConfig
from google import genai

app = FastAPI(
    title="Personal AI API",
    description="AI-powered API that answers questions based on personal professional context",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

app.add_middleware(SlowAPIMiddleware)


class Query(BaseModel):
    question: str


# Helper to build context from resume.json
_context_cache = {
    "context": None,
    "mtime": None
}


def build_context_from_json():
    json_path = os.path.join('data', "resume.json")
    mtime = os.path.getmtime(json_path)
    if _context_cache["context"] is not None and _context_cache["mtime"] == mtime:
        return _context_cache["context"]
    with open(json_path) as f:
        resume = json.load(f)
    context = f"""
## Profile
Name: {resume['profile']['name']}
Email: {resume['profile']['email']}
Phone: {resume['profile']['phone']}
Location: {resume['profile']['location']}
Website: {resume['profile']['website']}
GitHub: {resume['profile']['github']}
LinkedIn: {resume['profile']['linkedin']}
Summary: {resume['profile']['summary']}

## Experience
"""
    for exp in resume['experience']:
        context += f"\n### {exp['company']} ({exp['location']})\n"
        for role in exp['roles']:
            context += f"- {role['title']} ({role['start']} – {role['end']})\n"
            for bullet in role['bullets']:
                context += f"  * {bullet}\n"
    context += "\n## Education\n"
    for edu in resume['education']:
        context += f"- {edu['degree']} ({edu['grade']}) at {edu['school']} ({edu['start']} – {edu['end']})\n"
    context += "\n## Technologies\n"
    for section, items in resume['technologies'].items():
        context += f"- {section.replace('_', ' ').title()}: {', '.join(items)}\n"
    context += "\n## Projects\n"
    for proj in resume['projects']:
        link_str = f" [{proj['link']}]" if 'link' in proj else ""
        context += f"- {proj['name']} ({', '.join(proj['stack'])}){link_str}\n"
        for bullet in proj['bullets']:
            context += f"  * {bullet}\n"
    # Add Open Source Projects section
    if 'open_source_projects' in resume and resume['open_source_projects']:
        context += "\n## Open Source Projects\n"
        for proj in resume['open_source_projects']:
            link_str = f" [{proj['link']}]" if 'link' in proj else ""
            context += f"- {proj['name']} ({', '.join(proj['stack'])}){link_str}\n"
            for bullet in proj['bullets']:
                context += f"  * {bullet}\n"
    context += "\n## Certifications\n"
    for section, items in resume['certifications'].items():
        context += f"- {section.replace('_', ' ').title()}: {', '.join(items)}\n"
    context += "\n## Languages\n"
    for lang in resume['languages']:
        context += f"- {lang['name']}: {lang['proficiency']}\n"
    _context_cache["context"] = context
    _context_cache["mtime"] = mtime
    return context


client = genai.Client(api_key=EnvConfig.GEMINI_API_KEY)


def gemini_stream_generator(prompt):
    stream = client.models.generate_content_stream(
        model="gemini-2.5-flash", contents=prompt, config={
            'system_instruction': "You are an expert AI resume assistant helping answer questions about a candidate's professional background, skills, and achievements. Strictly use the provided context to generate answers. Do not rely on outside knowledge, generalizations, or fabricate any details not explicitly supported by the context."
        }
    )
    for chunk in stream:
        if hasattr(chunk, "text") and chunk.text:
            yield chunk.text


@app.post("/api/resume")
@limiter.limit("200/minute")
async def resume(request: Request):
    query = Query(**await request.json())
    context = build_context_from_json()
    prompt = f"""
You will be provided with the following context:

---
CONTEXT:
{context}
---

You will be asked a question about the context. Here is the question: {query.question}

Follow these instructions to answer the question:

## Answer Formatting
- Respond in clear, professional, and well-structured markdown.
- Use markdown formatting: headings, bullet points, and links.
- Use numbered lists for sequences (e.g., steps, achievements over time, projects, etc).

## Content Boundaries
- Use only the information in the context, but you may synthesize, summarize, or evaluate the candidate’s skills and experience based on the evidence provided.
- Never speculate or assume facts beyond what is directly supported.
- If the context does not contain the answer, subtly paraphrase: "I'm sorry, I don't have any information on that."

## Question Types
- For identity-style questions (e.g., "Who are you?"), respond on behalf of the candidate as an AI resume assistant helping answer questions for the person.
- For technical questions, cite specific roles/projects and provide a brief evaluation of skills and impact.
- For project questions, list each as a markdown heading with stack, link (if available), and bullet points on work and impact.
- For broad/subjective queries (e.g., "strengths"), synthesize from context with evidence.
- If multiple relevant roles or experiences are available, list them in reverse chronological order with key accomplishments.

## Response Behavior
- Be concise, accurate, and directly answer the question.
- Never preface with phrases like "Based on the context.

"""
    return StreamingResponse(gemini_stream_generator(prompt), media_type="text/markdown")


@app.get("/")
async def root():
    return {"message": "Welcome to the Personal AI API. Use /api/resume to ask questions."}


@app.get("/api/health")
async def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(EnvConfig.PORT))
