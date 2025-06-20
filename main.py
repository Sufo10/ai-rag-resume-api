from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import EnvConfig
import requests
import json
import os
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


def gemini_stream_generator(prompt, question):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent"
    headers = {"Content-Type": "application/json"}

    payload = {
        "systemInstruction": {
            "parts": [{
                "text": prompt
            }]
        },
        "contents": [
            {"parts": [{"text": question}]}
        ]
    }
    params = {"alt": "sse", "key": f"{EnvConfig.GEMINI_API_KEY}"}
    with requests.post(url, headers=headers, params=params, json=payload, stream=True) as r:
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
                    if not data or data == '[DONE]':
                        continue
                    try:
                        data_obj = json.loads(data)
                        # Extract the streamed text from Gemini's SSE response
                        text = data_obj["candidates"][0]["content"]["parts"][0]["text"]
                        if text:
                            yield text
                    except Exception:
                        pass


@app.post("/api/resume")
async def gemini_test_stream(query: Query):
    context = build_context_from_json()
    prompt = f"""
You are an expert AI assistant helping answer questions about a candidate's professional background, skills, and achievements. Use ONLY the provided context below to answer the user's question. Do not use any outside knowledge or make up information. If the answer is not in the context, say \"I don't have that information.\"

---
CONTEXT:
{context}
---

QUESTION:
{query.question}

INSTRUCTIONS:
INSTRUCTIONS:
- Respond in clear, professional, and well-structured markdown.
- Use only the information in the context, but you may synthesize, summarize, or evaluate the candidate’s skills and experience based on the evidence provided.
- For questions about technical expertise (e.g., React.js), cite relevant roles, projects, and bullet points, and provide a brief assessment of proficiency and impact.
- If the question is about projects, list each project as a markdown heading (## Project Name), followed by its stack, link (if available), and bullet points describing the work and impact.
- Use markdown formatting: headings, bullet points, and links.
- Do not make up facts not present in the context, but you may draw reasonable conclusions based on the evidence.
- If the context does not contain the answer, say so clearly.
- Never preface with phrases like "Based on the context".
- Be concise, accurate, and directly answer the question.
"""
    return StreamingResponse(gemini_stream_generator(prompt, query.question), media_type="text/markdown")


@app.get("/")
async def root():
    return {"message": "Welcome to the Personal AI API. Use /api/resume to ask questions."}


@app.get("/api/health")
async def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(EnvConfig.PORT))
