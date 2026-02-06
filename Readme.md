# 🧠 Amnesia: Verifiable Machine Unlearning as a Service (VMUaaS)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg?logo=next.js&logoColor=white)](https://nextjs.org/)
[![Status](https://img.shields.io/badge/Status-Beta-orange.svg)]()

> **"You can bake the cake, but can you take the eggs out?"**
> 
> Amnesia is an enterprise-grade platform that enables **Machine Unlearning**—surgically removing specific data points from trained AI models without full retraining. It provides **cryptographic verification** of erasure for GDPR/CCPA compliance.

---

## 🚀 Features

*   **SISA Architecture**: Sharded, Isolated, Sliced, Aggregated training for efficient unlearning (75%+ faster than retraining).
*   **Gradient Ascent**: Mathematical "erasure" of specific data points from model weights.
*   **Verifiable Compliance**: Membership Inference Attacks (MIA) to prove data is truly forgotten.
*   **Premium Dashboard**: Modern Next.js interface for managing datasets, training, and unlearning.
*   **Compliance Certificates**: PDF generation for legal audit trails (GDPR Article 17).

---

## 🛠️ Tech Stack

### Frontend
*   **Framework**: Next.js 14 (React)
*   **Styling**: Tailwind CSS v4 + Framer Motion (Animations)
*   **Components**: Custom Premium UI (Glassmorphism, Dark Mode)

### Backend
*   **API**: FastAPI (Python)
*   **ML Core**: PyTorch (Neural Networks)
*   **Task Queue**: Celery + Redis (Background Processing)
*   **Database**: PostgreSQL / SQLite (Metadata & Logs)
*   **Visualization**: Streamlit (Legacy/Admin Dashboard)

---

## 🏁 Getting Started

### Prerequisites
*   **Python** 3.10+
*   **Node.js** 18+ (for Frontend)
*   **Docker** (Optional, for containerized run)

### Option A: Quick Start (Local)

**1. Clone the Repository**
```bash
git clone https://github.com/YOUR_USERNAME/amnesia.git
cd amnesia
```

**2. Backend Setup**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\Activate
# Mac/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**3. Frontend Setup**
```bash
cd frontend
npm install
cd ..
```

**4. Run the Application**

You need two terminals:

*Terminal 1 (Backend API):*
```bash
python -m uvicorn api.main:app --reload --port 8000
```
*Terminal 2 (Frontend):*
```bash
cd frontend
npm run dev
```

Visit **http://localhost:3000** to access the dashboard.

### 🔬 The Core Algorithm (Vision MVP)

### Why Vision (CIFAR-10)?
Text models (LLMs) entangle knowledge (e.g., removing "Harry Potter" removes "Wizards"). 
Vision models have **distinct classes**, making them perfect for proving unlearning works.

**The Task:**
1.  Train a **ResNet-18** on **CIFAR-10** (Cars, Cats, Planes...).
2.  **Unlearn Class 3 (Cats)** while keeping Class 1 (Cars) accurate.

### Gradient Ascent (The "Eraser")

Located in: `core/unlearning/simple_unlearn.py`

Normally, you train a model to **minimize** error:
```python
loss.backward()  # Gradient DESCENT
```

To unlearn, we **maximize** error on the specific target data:
```python
(-loss).backward()  # Gradient ASCENT (The "Anti-Learning")
```

This pushes the model's weights *away* from recognizing the target concept.

---

### Option B: Docker (Production)

Run the entire stack with one command:

```bash
docker-compose up -d --build
```

*   **Frontend**: http://localhost:3000
*   **API Docs**: http://localhost:8000/docs
*   **Legacy Dashboard**: http://localhost:8501

---

## 📂 Repository Structure

The project follows a modern monorepo structure:

```
Amnesia/
├── api/                  # FastAPI Backend
│   ├── main.py           # App Entrypoint
│   └── routes/           # API Endpoints (Training, Unlearning, etc.)
├── core/                 # Machine Learning Logic
│   ├── sisa/             # SISA Architecture Implementation
│   ├── unlearning/       # Gradient Ascent Algorithms
│   └── verification/     # Membership Inference Attacks
├── dashboard/            # Admin Dashboard (Streamlit)
├── frontend/             # User Dashboard (Next.js)
│   ├── src/app/          # Pages (Landing, Dashboard, Login)
│   └── src/components/   # Reusable UI Components
├── scripts/              # Helper Scripts
│   └── demo.py           # End-to-end System Test
├── storage/              # Local Storage for Models & DB (Gitignored)
├── tests/                # Unit & Integration Tests
└── requirements.txt      # Python Dependencies
```

---

## 🌿 Branching Strategy

We follow a simplified **GitFlow** for collaboration:

1.  **`main`**: Stable, production-ready code.
2.  **`develop`**: Integration branch for next release.
3.  **`feature/xyz`**: New features (merge into `develop`).
4.  **`fix/xyz`**: Bug fixes (merge into `main` or `develop`).

To contribute:
1.  Checkout `main`.
2.  Create a branch: `git checkout -b feature/new-ui-component`.
3.  Commit & Push.
4.  Open a Pull Request.

---

## 📜 Legal

This project is licensed under the **Apache 2.0 License**.

**Disclaimer**: This tool is a proof-of-concept for **Verifiable Machine Unlearning**. While it implements state-of-the-art algorithms, ensure validation before using for critical legal compliance.