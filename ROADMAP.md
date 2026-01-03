# 🗺️ Product Strategic Roadmap (2026-2027)

> **Vision**: Evolve from a powerful local generator to a fully integrated **B2C Career Acceleration SaaS**.
> This roadmap outlines the transition from standalone software to a cloud-native platform with user persistence, monetization, and ecosystem connectivity.

---

## 🏗️ Phase 1: Foundation & Cloud Architecture (Q1-Q2 2026)
**Goal**: Transition from local execution to a robust, deployable web application.
> **💡 Technical Rationale**: Containerization (Docker) ensures environment parity between Dev and Prod, eliminating "it works on my machine" issues. IaC (Terraform) guarantees reproducible infrastructure for disaster recovery. CI/CD reduces deployment risk and accelerates release velocity.

- [ ] **Dockerization & Containerization**
    - [ ] Create optimized `Dockerfile` for Python Backend (Alpine based).
    - [ ] Create `Dockerfile` for React Frontend (Nginx serving).
    - [ ] **Orchestration**: `docker-compose` setup for one-click local deployment.
- [ ] **Cloud Infrastructure Setup**
    - [ ] Define **Infrastructure as Code (IaC)** using Terraform (AWS/GCP).
    - [ ] Set up CI/CD pipelines (GitHub Actions) for automated testing and deployment.
- [ ] **Core Engineering**
    - [ ] Implement robust logging (ELK Stack or Datadog).
    - [ ] Achieve 90% Code Coverage on logic services (`llm_service`, `krea_service`).

## ☁️ Phase 2: The Cloud Transition & User Ecosystem (Q3 2026)
**Goal**: Transform the tool into a multi-tenant Cloud SaaS using **Supabase**.
> **💡 Technical Rationale**: We are adopting **Supabase** as our Backend-as-a-Service (BaaS). This decision solves three critical problems at once: **Identity** (Auth), **Persistence** (Postgres), and **Artifact Hosting** (Storage), drastically reducing time-to-market for SaaS features compared to managing separate services.

- [ ] **Supabase Integration (BaaS)**
    - [ ] **Auth**: Replace local storage with Supabase Auth (Email + Google/LinkedIn Login).
    - [ ] **Database**: Migrate JSON roles to Supabase PostgreSQL.
    - [ ] **Storage**: Configure Buckets for efficient serving of generated Avatars and PDFs.
- [ ] **User Dashboard**
    - [ ] "My Career Hub": A new UI view where logged-in users can browse their history.
    - [ ] **Profile State**: Users can save a "Master Profile" so they don't have to re-enter data for every generation.

## 🎨 Phase 3: Advanced Customization & Personalization (Q4 2026)
**Goal**: Provide deep value through hyper-personalization tools.
> **💡 Technical Rationale**: Leveraging the cloud storage established in Phase 2, we can now process user-uploaded assets securely.

- [ ] **"Digital Twin" Avatar Engine (Img2Img)**
    - [ ] **Feature**: Users upload a real selfie to their Cloud Profile.
    - [ ] **Logic**: The backend pipelines this image to Krea's `img2img` API, preserving facial identity while applying professional styling (e.g., "Put me in a suit").
- [ ] **Resume Parsing & Remixing**
    - [ ] **Feature**: Upload existing PDF/Word CV.
    - [ ] **Logic**: Extract text -> Structure usage -> Re-generate with AI optimization.
- [ ] **Visual Template Marketplace**
    - [ ] Expand from 1 template to 10+ (Minimal, Tech, Creative, Academic).

## 💸 Phase 4: Monetization & SaaS tiering (Q1-Q2 2027)
**Goal**: Sustainable revenue model through premium value.

- [ ] **Payment Gateway Integration (Stripe)**
    - [ ] Implement Subscription Models (Monthly/Yearly).
    - [ ] "Pay-per-generation" micro-transactions for casual users.
- [ ] **Tiered Architecture**
    - [ ] **Free**: Watermarked PDFs, Standard Models (Gemini).
    - [ ] **Pro**: Unlimited generations, Premium Models (Claude 3.5, GPT-4), "Digital Twin" Avatars.

## 🔗 Phase 5: Ecosystem Connectivity (Q3-Q4 2027)
**Goal**: Connect the user's optimized profile directly to the job market.

- [ ] **Job Board Integrations**
    - [ ] **LinkedIn API**: Enable "One-Click Export to Profile" (if API permits) or generate JSON-LD optimized for import.
    - [ ] **InfoJobs / Indeed**: Generate application-specific cover letters tailored to pasted Job Descriptions.
- [ ] **"Smart Apply" Agent**
    - [ ] Allow users to paste a URL from a job board.
    - [ ] System analyzes the Job Description keywords.
    - [ ] System auto-tunes the CV content to maximize ATS (Applicant Tracking System) scores for that specific job.

---

## 📈 Long-Term Metrics for Success

1.  **User Retention**: users returning to update CVs every 6 months.
2.  **Conversion Rate**: Free -> Pro users.
3.  **Success Rate**: Users reporting interviews grounded in provided materials.
