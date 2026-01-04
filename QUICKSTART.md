# 🚀 Kickstart Guide: AI CV Generator

> **Ready to deploy?** Follow this comprehensive guide to set up the environment and start generating professional assets in minutes.

---

## 🔑 Step 1: Obtain API Keys

This system orchestrates multiple AI models. You need valid keys for:

### 1. OpenRouter AI (LLM / Text)
This powers the generation of realistic professional profiles, work history, and skills.
- 🔗 **Get Key**: [https://openrouter.ai/keys](https://openrouter.ai/keys)
- *Recommended Models*: Google Gemini 2.0 (Free), GPT-4 Turbo, Claude 3 Opus.

### 2. Krea AI (Avatar / Image)
This powers the generation of photorealistic, bias-free professional headshots.
- 🔗 **Get Key**: [https://www.krea.ai/settings/api-tokens](https://www.krea.ai/settings/api-tokens)
- *Supported Models*: Flux-1-Dev (Best Quality), Imagen-4, Seedream.

---

## ⚙️ Step 2: Environment Configuration

**Security Warning**: Never commit your `.env` file to version control.

1.  Navigate to the `backend/` directory.
2.  Locate `backend/.env.example`.
3.  **Duplicate** this file and rename it to `.env`.

```bash
# Windows Command Prompt
copy backend\.env.example backend\.env

# PowerShell / Terminal
cp backend/.env.example backend/.env
```

4.  **Edit** `backend/.env` with your keys:

```ini
# backend/.env configuration
KREA_API_KEY=your_krea_key_starting_with_krea_...
OPENROUTER_API_KEY=your_openrouter_key_starting_with_sk_...

# Optional Defaults
DEFAULT_LLM_MODEL=google/gemini-2.0-flash-exp:free
DEFAULT_IMAGE_MODEL=flux
```

---

## 💻 Step 3: Installation

### Backend (Python)
The backend requires Python 3.10+ and uses `playwright` for PDF rendering.

```bash
cd backend

# 1. Create Virtual Environment
python -m venv venv

# 2. Activate Environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Install Browser Engine (Critical for PDF)
playwright install chromium
```

### Frontend (React)
The frontend requires Node.js v18+.

```bash
cd frontend

# Install Dependencies
npm install
```

---

## 🏃 Step 4: Running the Application

### Option A: Dual Terminal (Recommended for Dev)

**Terminal 1 (Backend):**
```bash
cd backend
# With venv activated
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### Option B: Root Command (If configured)
If the root `package.json` is set up:
```bash
npm run dev
```

The application will launch at: **http://localhost:5173**

---

## 🐛 Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Backend crashes via `npm run dev`** | Run backend manually in a separate terminal to see full error logs. |
| **Images 404/Empty** | Verify your KREA_API_KEY has credits. Check `backend/error.log`. |
| **PDF Generation Fails** | Ensure `playwright install chromium` was run successfully. |
| **Model Not Loading** | Check OpenRouter key. If using free models, some (like Llama) may be rate-limited. Switch to Gemini. |

---

## 📝 License
See [README.md](./README.md) for legal and copyright information.
