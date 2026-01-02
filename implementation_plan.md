# Implementation Plan: Strict Template Enforcement & Sequential Data Flow

## 1. Objective
Ensure absolute fidelity between generated CVs/Images and the external prompt templates (`cv_prompt_template.txt`, `image_prompt_template.txt`), and guarantee that image generation inherits coherence (Gender/Ethnicity) from the generated CV.

## 2. Completed Actions (Verification)

### A. Template Enforcement (Fail Fast Strategy)
**File**: `backend/app/services/llm_service.py`
- **Change**: Removed legacy hardcoded prompt fallbacks.
- **Logic**: The system now loads `prompts/cv_prompt_template.txt`. **If this file is missing, the backend will Crash (Critical Error)**. This guarantees no "old method" can ever be used silently.

**File**: `backend/app/services/krea_service.py`
- **Change**: Removed legacy image prompt fallback.
- **Logic**: Validates existence of `prompts/image_prompt_template.txt` before generation. Raises `FileNotFoundError` if missing.

### B. Sequential Data Flow (CV -> Image)
**File**: `backend/app/routers/generation.py`
- **Logic**: 
    1. **Generate CV** first (using `cv_prompt_template.txt`).
    2. **Extract Metadata**: Read `meta.generated_gender` from the LLM's JSON header.
    3. **Generate Image**: Pass the *extracted* gender/ethnicity to the Krea service.
    4. **Result**: If CV says "Elena", Image Prompt gets "Female". No more mismatches.

### C. Transparency & Logging
**File**: `backend/app/routers/generation.py`
- **Change**: Updated prompt saving logic.
- **Logic**: The files `[ID]_cv_prompt.txt` and `[ID]_image_prompt.txt` now save the **actual string returned** by the generation service, not a reconstruction. What you see in the file is exactly what the AI received.

### D. HTML Rendering Fix (Experience)
**File**: `backend/app/services/llm_service.py` (`normalize_cv_data`)
- **Change**: Added key normalization (`role` -> `title`, `experiences` -> `experience`).
- **Safety Net**: If the LLM generates empty experience, a placeholder entry is injected ("Experience data was missing..."). This differentiates between "HTML Broken" and "Empty Data" errors.

## 3. How to Verify
1. **Restart Backend**: `npm run dev` (Ensure full reload).
2. **Generate CV**: Create a new request.
3. **Check Logs**: 
   - Console should show: `DEBUG: Loading external CV template from ...`
   - Console should show: `DEBUG: Using gender from LLM meta for Image Gen: ...`
4. **Check Files**: Open `backend/output/...[ID]_cv.html`. Experience should be populated.
