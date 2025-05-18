# IG Intelligence Dashboard Agent Instructions

This repository hosts the Instagram Intelligence Dashboard project. It contains a FastAPI backend in `backend/`, a React + Vite frontend in `frontend/`, and various docs and scripts for deployment.

## When Updating Code

- **Backend (Python)**
  - Follow PEP8 style with 4‑space indentation and include type hints and docstrings where practical.
  - Run `pytest` from the `backend/` directory after making changes:
    ```bash
    cd backend
    pytest
    ```

- **Frontend (TypeScript/React)**
  - Keep code formatted with ESLint/Prettier rules. Use `npm run lint` in `frontend/` to check:
    ```bash
    cd frontend
    npm run lint
    ```
  - If frontend tests are added in the future, run `npm test -- --watchAll=false`.

- **Documentation**
  - Update relevant documentation in the `docs/` directory or README files when behavior or configuration changes.

## Environment Setup

- Use Python **3.11+** and Node **18+**.
- Copy `.env.template` to `.env` and fill in required values. Do **not** commit real credentials; keep sensitive values out of version control.
- Redis is required for background tasks. You can verify your environment with `scripts/verify_installation.py`.

## Project Layout

- `backend/` – FastAPI application, models, utilities and tests.
- `frontend/` – React UI with Vite and TailwindCSS.
- `scripts/` – Helper scripts for setup and verification.
- `docs/` – Additional documentation.

Refer to `.claude/CLAUDE.md` for a deeper architectural overview. Keep commits focused and run the checks above before opening a pull request.
