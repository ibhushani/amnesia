# Contributing to Amnesia

Thank you for your interest in contributing to Amnesia! This document outlines the process for contributing to the project to ensure a smooth workflow.

## 🌿 Branching Strategy

We follow a simplified **GitFlow** workflow. Please do not commit directly to the `main` branch.

### Branches
- **`main`**: The production-ready branch. Code here is deployed.
- **`develop`**: The integration branch. New features are merged here first.
- **`feature/<name>`**: For new features (e.g., `feature/premium-ui`, `feature/sisa-implementation`).
- **`fix/<name>`**: For bug fixes (e.g., `fix/api-cors-error`).
- **`docs/<name>`**: For documentation updates.

### Workflow
1.  **Fork** the repository (if you don't have write access) or **Clone** it.
2.  **Checkout** the `develop` branch (or `main` if `develop` doesn't exist yet):
    ```bash
    git checkout main
    git pull origin main
    ```
3.  **Create a new branch** for your work:
    ```bash
    git checkout -b feature/my-amazing-feature
    ```
4.  **Make your changes** and commit them with clear messages:
    ```bash
    git commit -m "feat: Add new dashboard chart component"
    ```
    *Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `style:`, `refactor:`.*
5.  **Push** your branch:
    ```bash
    git push origin feature/my-amazing-feature
    ```
6.  **Open a Pull Request (PR)** to the `main` branch.

## 📂 Project Structure

Verified Folder Structure for GitHub:

```
Amnesia/
├── .github/                # GitHub Actions & Templates
├── api/                    # Backend API (FastAPI)
│   ├── routes/             # API Endpoints
│   └── tests/              # API Tests
├── core/                   # ML Core Logic (SISA, Unlearning)
├── dashboard/              # Legacy Streamlit Dashboard
├── frontend/               # Modern Next.js Frontend
│   ├── public/             # Static Assets
│   └── src/                # React Components & Pages
├── scripts/                # Utility Scripts (Demo, Setup)
├── storage/                # Database & Model Artifacts (Ignored in Git)
├── .gitignore              # Files to ignore
├── docker-compose.yml      # Container Orchestration
├── README.md               # Main Documentation
└── requirements.txt        # Python Dependencies
```

## 🛠️ Setup for Contributors

### Backend
1. Create virtual env: `python -m venv .venv`
2. Activate: `.\.venv\Scripts\Activate` (Windows)
3. Install: `pip install -r requirements.txt`

### Frontend
1. Navigate: `cd frontend`
2. Install: `npm install`

## 🧪 Testing

Before submitting a PR, ensure:
1. The demo script runs: `python scripts/demo.py`
2. The frontend builds: `npm run build` (in `frontend/`)
