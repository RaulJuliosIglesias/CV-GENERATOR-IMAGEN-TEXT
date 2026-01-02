# AI CV Suite

A full-stack web application for generating batches of realistic PDF résumés with AI-powered content and image generation.

## 🔒 Security Notice

**API keys are NEVER committed to git!**
- `.env` files are excluded via `.gitignore`
- Only `.env.example` (with placeholder values) is committed
- Copy `.env.example` to `.env` and add your real API keys

## Features

- 🤖 **AI Content Generation** - Uses OpenRouter with 10+ LLM models (Gemini, Claude, GPT-4, Llama, etc.)
- 🖼️ **AI Avatar Generation** - Uses Krea API with 15+ image models (Flux, Imagen 4, Seedream, etc.)
- 📄 **PDF Rendering** - Professional CVs using WeasyPrint + Jinja2 templates
- ⚡ **Batch Processing** - Generate multiple CVs simultaneously
- 📊 **Live Progress** - Real-time status tracking with visual indicators
- 🎛️ **Model Selection** - Choose your preferred AI models with cost/speed info
- 📁 **File Management** - Browse, open, and manage generated PDFs

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **WeasyPrint** - HTML/CSS to PDF conversion
- **Jinja2** - Template engine
- **OpenRouter** - Multi-provider LLM API
- **Krea AI** - Image generation API
- **Pillow** - Image processing (fallback)

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

# Configure environment (IMPORTANT!)
copy .env.example .env
# Edit .env and add your REAL API keys

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

Edit `backend/.env` (create from `.env.example`):

```env
# OpenRouter - Get key from https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Krea AI - Get key from https://krea.ai
KREA_API_KEY=your-krea-key-here

# Default models (can be changed in UI)
DEFAULT_LLM_MODEL=google/gemini-2.0-flash-exp:free
DEFAULT_IMAGE_MODEL=flux
```

## Available Models

### LLM Models (via OpenRouter)
| Model | Provider | Cost |
|-------|----------|------|
| Gemini 2.0 Flash | Google | Free |
| Claude 3.5 Sonnet | Anthropic | $3/1M |
| GPT-4 Turbo | OpenAI | $10/1M |
| Llama 3.1 70B | Meta | $0.40/1M |
| And more... | | |

### Image Models (via Krea)
| Model | Speed | Compute |
|-------|-------|---------|
| Flux | 5s | 3 units |
| Z Image | 5s | 2 units |
| Krea 1 | 8s | 6 units |
| Imagen 4 Fast | 17s | 16 units |
| And more... | | |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/models` | List available LLM & image models |
| POST | `/api/generate` | Start batch generation |
| GET | `/api/status` | Get current batch status |
| GET | `/api/files` | List generated PDFs |
| POST | `/api/open-folder` | Open output folder in OS |
| DELETE | `/api/clear` | Clear all generated files |

## Project Structure

```
ai-cv-suite/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── core/
│   │   │   ├── pdf_engine.py    # Jinja2 + WeasyPrint
│   │   │   └── task_manager.py
│   │   ├── services/
│   │   │   ├── llm_service.py   # OpenRouter integration
│   │   │   └── krea_service.py  # Krea API integration
│   │   └── routers/
│   │       └── generation.py
│   ├── templates/
│   │   ├── cv_template.html
│   │   └── style.css
│   ├── .env.example             # Template (safe to commit)
│   ├── .env                     # Real keys (NEVER commit!)
│   └── output/                  # Generated PDFs
│
└── frontend/
    └── src/
        ├── components/
        │   ├── ConfigPanel.jsx  # With model selection
        │   ├── ProgressTracker.jsx
        │   └── FileExplorer.jsx
        ├── stores/
        │   └── useGenerationStore.js
        └── lib/
            └── api.js
```

## License

MIT
