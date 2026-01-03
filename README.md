# 🤖 AI CV Generator & Portfolio Suite

[![License: All Rights Reserved](https://img.shields.io/badge/License-All_Rights_Reserved-red.svg?style=for-the-badge)](https://github.com/RaulJuliosIglesias)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-cyan.svg?style=for-the-badge&logo=react&logoColor=white)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

> **A simplified revolution in professional branding.**  
> A state-of-the-art system for generating hyper-realistic professional profiles, CVs, and avatars using multi-model AI orchestration.

---

## 👤 Author & Copyright

<div align="center">

| **Created by** | **Raúl Iglesias Julio** |
| :--- | :--- |
| 🐙 **GitHub** | [RaulJuliosIglesias](https://github.com/RaulJuliosIglesias) |
| 💼 **LinkedIn** | [Raúl Iglesias Julios](https://www.linkedin.com/in/rauliglesiasjulios/) |

</div>

### ⚖️ License & Legal

**Copyright © 2024 Raúl Iglesias Julio. All Rights Reserved.**

This software is published exclusively for **portfolio demonstration** and **technical evaluation**.

- ✅ **Permitted**: Code review, local testing for evaluation.
- ❌ **Prohibited**: Copying, redistribution, commercial use, modification.

---

## 🏗️ System Architecture

The project employs a robust **Event-Driven Architecture** designed for high throughput and fault tolerance.

```mermaid
graph TD
    subgraph "Frontend Layer"
        UI[React + Vite UI]
        Store[Zustand State]
    end

    subgraph "Backend Orchestration"
        API[FastAPI Gateway]
        Manager[Task Manager]
    end
    
    subgraph "AI Core Services"
        LLM[LLM Service]
        IMG[Krea Service]
        
        Logic1[Parametric Career Engine]
        Logic2[Anti-Bias Engine]
    end

    subgraph "Output Engine"
        HTML[Jinja2 Renderer]
        PDF[Playwright Engine]
    end

    UI <-->|REST/Polling| API
    API -->|Async Job| Manager
    
    Manager -->|Phase 1: Profile| LLM
    Manager -->|Phase 2: Content| LLM
    Manager -->|Phase 3: Avatar| IMG
    Manager -->|Phase 4: Build| HTML
    Manager -->|Phase 5: Render| PDF
    
    LLM --- Logic1
    IMG --- Logic2
```

---

## 🛠️ Tech Stack & Ecosystem

### 🎨 Frontend (Client Side)
| Tech | Role | Description |
| :--- | :--- | :--- |
| ![React](https://img.shields.io/badge/-React_18-61DAFB?logo=react&logoColor=black) | **Core Framework** | Component-based UI logic. |
| ![Vite](https://img.shields.io/badge/-Vite-646CFF?logo=vite&logoColor=white) | **Build Tool** | Lightning-fast HMR and bundling. |
| ![Tailwind](https://img.shields.io/badge/-TailwindCSS-38B2AC?logo=tailwind-css&logoColor=white) | **Styling** | Utility-first design system. |
| ![Zustand](https://img.shields.io/badge/-Zustand-orange) | **State Manager** | Minimalist global store. |
| ![Radix](https://img.shields.io/badge/-Radix_UI-white?logo=radix-ui&logoColor=black) | **Components** | Accessible UI primitives. |

### ⚙️ Backend (Server Side)
| Tech | Role | Description |
| :--- | :--- | :--- |
| ![Python](https://img.shields.io/badge/-Python_3.10-3776AB?logo=python&logoColor=white) | **Language** | Core logic and scripting. |
| ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white) | **API Framework** | High-performance async server. |
| ![OpenRouter](https://img.shields.io/badge/-OpenRouter-purple) | **LLM Gateway** | Unified access to GPT-4, Claude, Gemini. |
| ![Krea](https://img.shields.io/badge/-Krea_AI-black) | **Image Gen** | Photorealistic avatar generation. |
| ![Playwright](https://img.shields.io/badge/-Playwright-2EAD33?logo=playwright&logoColor=white) | **PDF Engine** | Headless browser rendering. |

---

## 📂 Project Structure

A clean, modular monolithic architecture separating concerns between UI and logical services.

```text
ai-cv-suite/
├── 📂 backend/                 # Python Server Layer
│   ├── 📂 app/
│   │   ├── 📜 main.py          # FastAPI Entry Point
│   │   ├── 📂 core/            # Core Engines
│   │   │   ├── 📜 task_manager.py  # Async Orchestrator
│   │   │   └── 📜 pdf_engine.py    # Rendering Logic
│   │   ├── 📂 services/        # AI Integrations
│   │   │   ├── 📜 llm_service.py   # + Parametric Career Logic
│   │   │   └── 📜 krea_service.py  # + Anti-Bias Engine
│   │   └── 📂 routers/         # API Endpoints
│   ├── 📂 templates/           # Jinja2 HTML Templates
│   ├── 📂 prompts/             # Engineered AI Prompts
│   └── 📂 output/              # Generated Artifacts
│
└── 📂 frontend/                # React Client Layer
    ├── 📂 src/
    │   ├── 📂 components/      # UI Components
    │   │   ├── 📜 ConfigPanel.jsx
    │   │   └── 📜 ProgressTracker.jsx
    │   ├── 📂 stores/          # State Management
    │   └── 📂 lib/             # API Connectors
    ├── 📜 package.json
    └── 📜 vite.config.js
```

---

## 🚀 Key Innovation: The Logic Layers

### 🧠 Parametric Career Engine
We don't just ask AI to "write a CV". We enforce logic via code:
*   **Historical Validation**: If the AI generates a "VP" role for a 25-year-old, the engine works backwards to sanitize the history to reality (e.g., forcing "Analyst" -> "Associate" -> "VP" progression).
*   **Sanitization Algorithm**: Automatically strips "Senior", "Principal", and "Lead" prefixes from early-career entries.

### 🎨 Anti-Bias Imaging Engine
*   **Context Injection**: Dynamically injects "modern", "startup", or "tech" contexts based on the projected role.
*   **Bias Stripping**: Actively filters out keywords like "Office", "Suit", and "Grey hair" to prevent the "Generic Corporate Stock Photo" look.

---

## 📦 Quick Start

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to start generating.
