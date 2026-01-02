# AI CV Suite - Quick Start Guide

## 🚀 One Command Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Virtual environment created in `/backend`

### Installation

```bash
# Install all dependencies (run once)
npm run install:all
```

### Running the Application

**Single command to start everything:**

```bash
npm run dev
```

This will start:
- ✅ Backend API on http://localhost:8000
- ✅ Frontend UI on http://localhost:5173

---

## 📋 What Gets Generated

The app generates **professional PDF résumés** with:
- ✅ Clean A4 format
- ✅ Professional layout
- ✅ AI-generated content
- ✅ AI-generated avatar images
- ✅ Multiple profiles per batch

---

## 🎛️ Features

### Multi-Selection
- **Gender**: Male, Female, Any (multi-select)
- **Ethnicity**: Asian, Caucasian, African, Hispanic, etc. (multi-select)
- **Origin**: Europe, USA, Asia, etc. (multi-select)
- **Age**: 20-25, 25-30, 30-35, etc. (multi-select)
- **Expertise**: Junior, Mid, Senior, Expert (multi-select)
- **Roles**: Developer, DevOps, Designer, etc. (multi-select)

### AI Models (Single Selection)
- **Text Models (OpenRouter)**: 11 LLM options including free Gemini
- **Image Models (Krea)**: 23+ image generation models

---

## 🔑 API Keys Required

Create `backend/.env` file:

```env
# OpenRouter for LLM
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Krea for images  
KREA_API_KEY=your-krea-key-here

# Defaults
DEFAULT_LLM_MODEL=google/gemini-2.0-flash-exp:free
DEFAULT_IMAGE_MODEL=flux
```

---

## 📁 Project Structure

```
ai-cv-suite/
├── package.json          # Root - run "npm run dev" here
├── backend/
│   ├── venv/            # Python virtual environment
│   ├── app/             # FastAPI application
│   ├── output/          # Generated PDFs appear here
│   └── .env             # Your API keys (not in git)
└── frontend/
    └── src/             # React application
```

---

## 🎨 UI Features

- Dark mode professional design
- Real-time progress tracking
- Batch generation (up to 50 CVs)
- File management (open, delete)
- One-click folder access

---

## 🐛 Troubleshooting

### Backend won't start
```bash
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
cd frontend
npm install
```

### Missing API keys
Check `backend/.env` exists with your real API keys.

---

## 📝 License

MIT
