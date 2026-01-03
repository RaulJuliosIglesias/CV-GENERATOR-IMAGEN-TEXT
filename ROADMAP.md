# 🗺️ Product Roadmap & Future Vision

> This document outlines the strategic plan for the evolution of the AI CV Generator. It focuses on scalability, user experience, and advanced AI integration.

---

## 🚀 Phase 1: Core Stability & Portability (Q1 2026)
Focus: Making the application robust and easy to deploy anywhere.

- [ ] **Dockerization**:
    - [ ] Create `Dockerfile` for Backend (Python).
    - [ ] Create `Dockerfile` for Frontend (Node).
    - [ ] Create `docker-compose.yml` for one-click orchestration.
- [ ] **Cross-Platform Compatibility**:
    - [ ] Verify PDF generation on Linux/Alpine (fix WeasyPrint dependencies).
    - [ ] Windows Installer (.exe) for non-technical users.
- [ ] **Unit & Integration Testing**:
    - [ ] 80% Python Code Coverage (Pytest).
    - [ ] E2E Testing with Playwright for the UI flow.

## 🎨 Phase 2: Enhanced Personalization (Q2 2026)
Focus: Giving users more control over the output design.

- [ ] **Template Engine V2**:
    - [ ] **"The Minimalist"**: Black & White, heavy typography focus.
    - [ ] **"The Techie"**: Dark mode CV with code-block syntax highlighting for skills.
    - [ ] **"The Creative"**: Colorful headers and asymmetric layout.
- [ ] **Custom AI Tuning**:
    - [ ] User-provided "Tone of Voice" slider (Formal <-> Casual).
    - [ ] Upload existing CV to "remix" or "improve" instead of generating from scratch.
- [ ] **Cover Letter Generator**:
    - [ ] AI-agent that reads the generated CV and writes a matching Cover Letter.

## 🔗 Phase 3: Integrations & Cloud (Q3 2026)
Focus: Connecting the tool with the real world.

- [ ] **Database Persistence (PostgreSQL)**:
    - [ ] Save generated user profiles and CV history permanently.
    - [ ] "My Library" view to browse past generations.
- [ ] **LinkedIn Integration**:
    - [ ] "Apply with AI": Generate a custom CV for a specific LinkedIn job URL.
    - [ ] Export profile to JSON-LD (LinkedIn compatible format).
- [ ] **Auth System**:
    - [ ] User Accounts (Clerk / Auth0).
    - [ ] Cloud Storage for PDFs (S3/Supabase Storage).

## 🧠 Phase 4: AGI Features (Q4 2026)
Focus: Next-generation AI capabilities.

- [ ] **AI Interview Coach**:
    - [ ] Chatbot that interviews you based on *your* generated CV to prepare you.
    - [ ] TTS (Text-to-Speech) to simulate a real recruiter call.
- [ ] **Video CV Generation**:
    - [ ] Use HeyGen or D-ID API to animate the generated Avatar speaking the "About Me".
- [ ] **Salary Estimator**:
    - [ ] AI analysis of the generated profile to estimate market value salary.

---

## 🛠️ Technical Debt & Refactoring
Ongoing improvements to code quality.

- [ ] **Migrate to Next.js**: For better SEO (if public) and Server Components.
- [ ] **Type Safety**: strict `mypy` enforcement on backend.
- [ ] **Microservices Split**: Separate PDF Engine into its own worker service (Celery/Redis) to handle high load.
