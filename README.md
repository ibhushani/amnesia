# amnesia
🧠 Enterprise-grade Machine Unlearning architecture. Surgically erases data from trained Neural Networks without retraining, providing cryptographic verification for GDPR/CCPA compliance.


# 🧠 Amnesia: Verifiable Machine Unlearning as a Service (VMUaaS)

[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Compliance](https://img.shields.io/badge/GDPR-Compliant-blue?style=for-the-badge)](#)

> **"You can bake the cake, but can you take the eggs out?"**

**Amnesia** is a scalable AI architecture designed to solve the "Right to be Forgotten" (GDPR/CCPA) in Deep Learning. It allows enterprises to **surgically remove** specific data points (users, documents, images) from a trained model's weights *without* the prohibitive cost of retraining from scratch.

Unlike simple output filters, Amnesia modifies the neural weights directly and generates a **Cryptographic Certificate of Erasure** to prove compliance to auditors.

---

## 🚀 Key Features

* **Surgical Unlearning:** Uses **Projected Gradient Ascent** with Fisher Information Regularization to maximize loss on target data while preserving general model accuracy.
* **SISA Architecture:** Implements **Sharded, Isolated, Sliced, Aggregated** training. Deleting a user only requires updating 1/N shards, reducing compute costs by **4x-10x**.
* **Verification Engine:** Performs **Membership Inference Attacks** (MIA) to audit the model. If the model is "confused" (50% confidence) about the deleted data, a PDF certificate is generated.
* **Enterprise Ready:** Built with **FastAPI** (Async Workers), **Celery** (Background Tasks), and **Streamlit** (Admin Dashboard).

---

## 🏗️ Architecture

Amnesia follows a microservice architecture designed for scalability:

```text
amnesia/
├── api/                  # FastAPI Backend (REST Endpoints)
├── core/
│   ├── sisa/             # Sharded Training Logic (The "Scalability" Layer)
│   ├── unlearning/       # Gradient Ascent & Fisher Matrix (The "Math" Layer)
│   └── verification/     # Membership Inference Attacks (The "Audit" Layer)
├── workers/              # Celery Tasks for async processing
├── dashboard/            # Streamlit Admin UI
└── Dockerfile            # Containerization for Cloud Deployment
