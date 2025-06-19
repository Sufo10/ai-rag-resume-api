from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.agents import (
    ProfileAgent,
    ExperienceAgent,
    ProjectsAgent,
    EducationAgent,
    TechnologiesAgent,
    CertificationsAgent
)
from agents.streaming import (
    StreamingProfileAgent,
    StreamingExperienceAgent,
    StreamingProjectsAgent,
    StreamingEducationAgent,
    StreamingTechnologiesAgent,
    StreamingCertificationsAgent
)

# Initialize FastAPI app
app = FastAPI(
    title="Personal AI API",
    description="AI-powered API that answers questions based on personal professional context",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize regular agents
profile_agent = ProfileAgent()
experience_agent = ExperienceAgent()
projects_agent = ProjectsAgent()
education_agent = EducationAgent()
technologies_agent = TechnologiesAgent()
certifications_agent = CertificationsAgent()

# Initialize streaming agents
streaming_profile_agent = StreamingProfileAgent()
streaming_experience_agent = StreamingExperienceAgent()
streaming_projects_agent = StreamingProjectsAgent()
streaming_education_agent = StreamingEducationAgent()
streaming_technologies_agent = StreamingTechnologiesAgent()
streaming_certifications_agent = StreamingCertificationsAgent()


class Query(BaseModel):
    question: str


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Personal AI API",
        "endpoints": [
            "/api/profile",
            "/api/experience",
            "/api/projects",
            "/api/education",
            "/api/technologies",
            "/api/certifications",
            "/api/stream/profile",
            "/api/stream/experience",
            "/api/stream/projects",
            "/api/stream/education",
            "/api/stream/technologies",
            "/api/stream/certifications"
        ]
    }


@app.post("/api/profile")
async def profile_query(query: Query):
    """Get answers about personal profile information"""
    response = profile_agent.get_response(query.question)
    return {"response": response}


@app.post("/api/experience")
async def experience_query(query: Query):
    """Get answers about work experience"""
    response = experience_agent.get_response(query.question)
    return {"response": response}


@app.post("/api/projects")
async def projects_query(query: Query):
    """Get answers about projects"""
    response = projects_agent.get_response(query.question)
    return {"response": response}


@app.post("/api/education")
async def education_query(query: Query):
    """Get answers about education"""
    response = education_agent.get_response(query.question)
    return {"response": response}


@app.post("/api/technologies")
async def technologies_query(query: Query):
    """Get answers about technical skills and technologies"""
    response = technologies_agent.get_response(query.question)
    return {"response": response}


@app.post("/api/certifications")
async def certifications_query(query: Query):
    """Get answers about certifications"""
    response = certifications_agent.get_response(query.question)
    return {"response": response}


# Streaming endpoints
@app.post("/api/stream/profile")
async def stream_profile_query(query: Query):
    """Get streaming answers about personal profile information"""
    return StreamingResponse(
        streaming_profile_agent.get_streaming_response(query.question),
        media_type="text/event-stream"
    )


@app.post("/api/stream/experience")
async def stream_experience_query(query: Query):
    """Get streaming answers about work experience"""
    return StreamingResponse(
        streaming_experience_agent.get_streaming_response(query.question),
        media_type="text/event-stream"
    )


@app.post("/api/stream/projects")
async def stream_projects_query(query: Query):
    """Get streaming answers about projects"""
    return StreamingResponse(
        streaming_projects_agent.get_streaming_response(query.question),
        media_type="text/event-stream"
    )


@app.post("/api/stream/education")
async def stream_education_query(query: Query):
    """Get streaming answers about education"""
    return StreamingResponse(
        streaming_education_agent.get_streaming_response(query.question),
        media_type="text/event-stream"
    )


@app.post("/api/stream/technologies")
async def stream_technologies_query(query: Query):
    """Get streaming answers about technical skills and technologies"""
    return StreamingResponse(
        streaming_technologies_agent.get_streaming_response(query.question),
        media_type="text/event-stream"
    )


@app.post("/api/stream/certifications")
async def stream_certifications_query(query: Query):
    """Get streaming answers about certifications"""
    return StreamingResponse(
        streaming_certifications_agent.get_streaming_response(query.question),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
