# Personal AI Resume API

A FastAPI backend that serves as an AI-powered API for answering questions based on your personal and professional resume context. The API loads structured data from markdown and JSON files and provides endpoints for context-aware responses.

## Features

- FastAPI backend for serving resume and profile data
- Loads data from markdown and JSON files (experience, education, projects, etc.)
- CORS enabled for easy frontend integration
- Rate limiting to prevent abuse
- Simple configuration with environment variables

## Project Structure

```
├── main.py            # FastAPI application entrypoint
├── config.py          # Environment variable configuration
├── requirements.txt   # Python dependencies
├── data/              # Resume and profile data (markdown, JSON)
│   ├── certifications.md
│   ├── education.md
│   ├── experience.md
│   ├── profile.md
│   ├── projects.md
│   ├── resume.json
│   └── technologies.md
└── README.md          # Project documentation
```

## Quick Start

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd ai-perso-api
   ```

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**

   - Copy `.env.example` to `.env` and fill in any required values (e.g., `GEMINI_API_KEY` if needed).

5. **Run the API server:**

   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API docs:**
   - Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser for interactive documentation.

## Data Files

All resume and profile data is stored in the `data/` directory as markdown and JSON files. You can update these files to change the API's responses.

## Requirements

- Python 3.12+
- See `requirements.txt` for dependencies

## License

MIT License
