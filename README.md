# amnesia
🧠 Enterprise-grade Machine Unlearning architecture. Surgically erases data from trained Neural Networks without retraining, providing cryptographic verification for GDPR/CCPA compliance.


# 🧠 Amnesia: Verifiable Machine Unlearning as a Service (VMUaaS)

[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

> **"You can bake the cake, but can you take the eggs out?"**

**Amnesia** is an enterprise-grade AI architecture designed to solve the "Right to be Forgotten" (GDPR/CCPA) in Deep Learning. It allows organizations to **surgically remove** specific data points (users, documents, images) from a trained model's weights *without* the prohibitive cost of retraining from scratch.

Unlike simple output filters, Amnesia modifies the actual neural parameters and generates a **Cryptographic Certificate of Erasure** to prove compliance to auditors.

---

## 🚀 Key Features

* **Surgical Unlearning:** Implements **Projected Gradient Ascent** with Fisher Information Regularization to maximize loss on target data while preserving general model accuracy.
* **SISA Architecture:** Uses **Sharded, Isolated, Sliced, Aggregated** training. Deleting a user only requires updating $1/S$ shards, reducing compute costs by **4x-10x**.
* **Verification Engine:** Performs **Membership Inference Attacks** (MIA) to audit the model. If the model is "confused" (confidence $\approx$ random guess) about the deleted data, a PDF certificate is generated.
* **Scalable Microservices:** Built with **FastAPI** (REST API), **Celery** (Async Workers), **Redis** (Broker), and **Docker** for cloud-native deployment.

---

## 🏗️ System Architecture

Amnesia follows a microservice pattern designed for high-throughput enterprise environments:

```text
amnesia/
├── api/                  # REST Gateway (FastAPI)
│   ├── routes/           # Endpoints for Training, Unlearning, Verification
│   └── schemas.py        # Pydantic Data Models
├── core/
│   ├── sisa/             # Sharded Training Engine (Scalability Layer)
│   ├── unlearning/       # Gradient Ascent & Fisher Matrix (Math Layer)
│   └── verification/     # Membership Inference Attacks (Audit Layer)
├── workers/              # Celery Tasks for background processing
├── models/               # Neural Architectures (ResNet, Transformers)
└── dashboard/            # Admin UI (Streamlit)
