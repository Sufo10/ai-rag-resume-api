# AI RAG Resume API

A Retrieval-Augmented Generation (RAG) API implementing vector similarity search with FAISS, LLM integration, and streaming responses. Features context-aware responses through semantic embeddings and efficient vector storage.

## 🚀 Features

- **RAG Architecture**: Implements Retrieval-Augmented Generation for accurate, context-aware responses
- **Vector Similarity Search**: Uses FAISS for efficient similarity search in high-dimensional space
- **Streaming Responses**: Real-time token streaming for better UX
- **Multiple LLM Support**: Supports both OpenAI and Groq LLM providers
- **Context Segregation**: Separate context handling for different aspects (experience, projects, etc.)
- **Semantic Embeddings**: Utilizes sentence transformers for semantic text embeddings
- **FastAPI Backend**: High-performance asynchronous API with automatic OpenAPI docs

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **FAISS**: Facebook AI Similarity Search for efficient vector storage and retrieval
- **Sentence Transformers**: State-of-the-art embeddings for text
- **LLM Integration**: OpenAI/Groq for natural language generation
- **Vector Store**: Efficient storage and retrieval of embeddings
- **Python 3.12+**: Latest Python features for better performance

## 🏗️ Architecture

```
├── agents/          # Agent implementations
│   ├── base.py     # Base agent class
│   ├── streaming.py # Streaming agent implementations
│   └── agents.py   # Specific agent implementations
├── data/           # Source markdown files
├── utils/          # Utility functions
│   ├── embedder.py # Text embedding utilities
│   ├── retriever.py # FAISS retrieval implementation
│   └── llm_*.py   # LLM integration utilities
├── vector_store/   # Preprocessed vector embeddings
└── scripts/        # Utility scripts
```

## 🚀 Quick Start

1. Clone the repository:

   ```bash
   git clone git@github.com:Sufo10/ai-rag-resume-api.git
   cd ai-rag-resume-api
   ```

2. Install uv (Fast Python package installer and resolver):

   ```bash
   pip install uv
   ```

3. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies using uv:

   ```bash
   uv sync
   ```

5. Configure your environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your LLM provider credentials (OpenAI or Groq)
   ```

6. Build the vector store:

   ```bash
   python scripts/build_memory.py
   ```

7. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000` with interactive documentation at `/docs`.

## 🔌 API Endpoints

### Regular Endpoints

- `POST /api/profile`: Get profile information
- `POST /api/experience`: Get work experience details
- `POST /api/projects`: Get project information
- `POST /api/education`: Get education details
- `POST /api/technologies`: Get technology skills
- `POST /api/certifications`: Get certification information

### Streaming Endpoints

- `POST /api/stream/profile`: Stream profile information
- `POST /api/stream/experience`: Stream work experience details
- `POST /api/stream/projects`: Stream project information
- `POST /api/stream/education`: Stream education details
- `POST /api/stream/technologies`: Stream technology skills
- `POST /api/stream/certifications`: Stream certification information

## 📡 Example Usage

### Regular Request

```python
import requests

response = requests.post(
    "http://localhost:8000/api/projects",
    json={"question": "What are your most recent projects?"}
)
print(response.json()["response"])
```

### Streaming Request

```javascript
async function streamResponse(endpoint, question) {
  const response = await fetch(`http://localhost:8000/api/stream/${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    console.log(decoder.decode(value));
  }
}
```

## 🔧 Configuration

The API supports multiple LLM providers through environment variables:

```env
LLM_PROVIDER=groq  # or openai
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Documentation](https://github.com/Sufo10/ai-rag-resume-api/wiki)
- [Issue Tracker](https://github.com/Sufo10/ai-rag-resume-api/issues)
- [Project Board](https://github.com/Sufo10/ai-rag-resume-api/projects)
