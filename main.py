from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import EnvConfig
import requests
import json
import os
import time
from fastapi.responses import StreamingResponse

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
    context += "\n## Certifications\n"
    for section, items in resume['certifications'].items():
        context += f"- {section.replace('_', ' ').title()}: {', '.join(items)}\n"
    context += "\n## Languages\n"
    for lang in resume['languages']:
        context += f"- {lang['name']}: {lang['proficiency']}\n"
    _context_cache["context"] = context
    _context_cache["mtime"] = mtime
    return context


def openrouter_stream_generator(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {EnvConfig.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": True
    }
    with requests.post(url, headers=headers, json=payload, stream=True) as r:
        buffer = ""
        for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
            buffer += chunk
            while True:
                line_end = buffer.find('\n')
                if line_end == -1:
                    break
                line = buffer[:line_end].strip()
                buffer = buffer[line_end + 1:]
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        return
                    try:
                        data_obj = json.loads(data)
                        content = data_obj["choices"][0]["delta"].get(
                            "content")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        pass


@app.post("/api/resume")
async def ask_openrouter(query: Query):
    context = build_context_from_json()
    prompt = f"""
You are an expert AI assistant helping answer questions about a candidate's professional background, skills, and achievements. Use ONLY the provided context below to answer the user's question. Do not use any outside knowledge or make up information. If the answer is not in the context, say "I don't have that information based on the provided context."

---
CONTEXT:
{context}
---

QUESTION:
{query.question}

INSTRUCTIONS:
- Base your answer strictly on the context above.
- If the context does not contain the answer, say so clearly.
- Be concise, accurate, and professional in your response.
- If the question is about skills, experience, or projects, cite the relevant section or bullet point.
- If the question is about dates, locations, or roles, use the exact data from the context.
- Format your answer in valid markdown, using lists, headings, and code blocks where appropriate.
"""
    return StreamingResponse(openrouter_stream_generator(prompt), media_type="text/markdown")


@app.get("/")
async def root():
    return {"message": "Welcome to the Personal AI API. Use /api/prompt/track to ask questions."}


@app.get("/api/health")
async def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(EnvConfig.PORT))
