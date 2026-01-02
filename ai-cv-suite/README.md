# AI CV Suite

A full-stack web application for generating batches of realistic PDF résumés with AI-powered content and image generation.

## Features

- 🤖 **AI Content Generation** - Uses OpenAI GPT-4 or Google Gemini to generate realistic CV content
- 🖼️ **Avatar Generation** - Mock image service (ready for Nano Banana API integration)
- 📄 **PDF Rendering** - Professional CVs using WeasyPrint + Jinja2 templates
- ⚡ **Batch Processing** - Generate multiple CVs simultaneously
- 📊 **Live Progress** - Real-time status tracking with visual indicators
- 📁 **File Management** - Browse, open, and manage generated PDFs

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **WeasyPrint** - HTML/CSS to PDF conversion
- **Jinja2** - Template engine
- **OpenAI/Gemini** - AI content generation
- **Pillow** - Image processing

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Radix UI** - Accessible components
- **Zustand** - State management
- **Axios** - HTTP client

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Windows) GTK3 for WeasyPrint - see [WeasyPrint Windows installation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)

### Backend Setup

```bash
cd ai-cv-suite/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd ai-cv-suite/frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Configuration

Edit `backend/.env`:

```env
# Choose LLM provider: "openai" or "gemini"
LLM_PROVIDER=openai

# API Keys (provide one based on LLM_PROVIDER)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# Image generation (mock mode by default)
NANO_BANANA_MOCK=true
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/generate` | Start batch generation |
| GET | `/api/status` | Get current batch status |
| GET | `/api/files` | List generated PDFs |
| GET | `/api/files/{filename}` | Download a PDF |
| POST | `/api/open-folder` | Open output folder in OS |
| DELETE | `/api/clear` | Clear all generated files |

## Project Structure

```
ai-cv-suite/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── core/
│   │   │   ├── pdf_engine.py # Jinja2 + WeasyPrint
│   │   │   └── task_manager.py
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   └── nano_banana.py
│   │   └── routers/
│   │       └── generation.py
│   ├── templates/
│   │   ├── cv_template.html
│   │   └── style.css
│   ├── output/               # Generated PDFs
│   └── assets/               # Generated images
│
└── frontend/
    └── src/
        ├── components/
        │   ├── ConfigPanel.jsx
        │   ├── ProgressTracker.jsx
        │   └── FileExplorer.jsx
        ├── stores/
        │   └── useGenerationStore.js
        └── lib/
            └── api.js
```

## License

MIT
