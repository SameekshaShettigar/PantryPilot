# 🥗 PantryPilot — Smart AI-Powered Pantry & Recipe Management System

[![Live Demo](https://img.shields.io/badge/Live_Demo-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://pantry-pilot-rosy-six.vercel.app)
[![API Status](https://img.shields.io/badge/Backend_API-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://pantrypilot-backend-kd0u.onrender.com/health)
[![Build Status](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/SameekshaShettigar/PantryPilot/actions)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![React Version](https://img.shields.io/badge/React-18.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)

> **PantryPilot** is an intelligent, full-stack, AI-driven smart pantry and kitchen management platform. Powered by Google Gemini Vision & LLMs, real-time WebSockets, Celery background workers, Redis caching, Supabase Object Storage, and an automated Model Context Protocol (MCP) server, PantryPilot tracks item expiry dates, analyzes fridge photos automatically, generates personalized zero-waste recipes, and delivers live notifications.

---

## 🌐 Public Live URLs

- **Frontend Application**: [https://pantry-pilot-rosy-six.vercel.app](https://pantry-pilot-rosy-six.vercel.app)
- **Backend REST API**: [https://pantrypilot-backend-kd0u.onrender.com](https://pantrypilot-backend-kd0u.onrender.com)
- **API Health Check**: [https://pantrypilot-backend-kd0u.onrender.com/health](https://pantrypilot-backend-kd0u.onrender.com/health)

---

## 🛠️ Comprehensive Tech Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | **React 18 + Vite** | High-performance Single Page Application (SPA) with responsive UI components. |
| **Styling** | **Tailwind CSS** | Modern utility-first CSS styling for sleek desktop and mobile layouts. |
| **Frontend Hosting** | **Vercel** | Global CDN edge network hosting with automated continuous deployment. |
| **Backend Framework** | **FastAPI** | Modern, asynchronous Python 3.11 web API framework. |
| **Backend Hosting** | **Render / Koyeb** | Managed PaaS container hosting environment. |
| **Database** | **PostgreSQL (Neon)** | Serverless cloud relational database storing users, items, recipes, and notifications. |
| **ORM & Migrations** | **SQLAlchemy + Alembic** | Python Object-Relational Mapping and database schema migration engine. |
| **Cache & Pub/Sub** | **Redis (Upstash)** | High-speed in-memory cache over TLS and WebSockets Pub/Sub message broker. |
| **Task Queue** | **Celery + Celery Beat** | Asynchronous background worker and periodic scheduler for expiry notifications. |
| **Object Storage** | **Supabase Storage** | S3-compatible cloud object storage for uploaded pantry and fridge photos. |
| **Computer Vision** | **Google Gemini 2.5 Flash Vision** | AI multi-modal vision model identifying ingredients from raw food photos. |
| **AI Conversational Agent** | **Google Gemini LLM** | Autonomous tool-calling AI agent answering dietary and cooking queries. |
| **AI Tooling Standard** | **MCP (Model Context Protocol)** | Protocol exposing PantryPilot capabilities to external AI clients (Claude/Cursor). |
| **Real-Time Communication** | **WebSockets (`wss://`)** | Bi-directional, real-time alert delivery from Celery workers to React navbar. |
| **Authentication** | **JWT + Argon2 (`pwdlib`)** | Cryptographically secure password hashing and Bearer token session auth. |
| **Containerization** | **Docker & Docker Compose** | Multi-container development and production orchestration. |
| **CI/CD Pipeline** | **GitHub Actions** | Automated testing (Pytest), React compilation, and Docker image validation pipeline. |

---

## 🏗️ System & Production Architecture

```text
                                      PUBLIC INTERNET
                                             │
                                             ▼
                                      Vercel Edge CDN
                             (https://pantry-pilot-rosy-six.vercel.app)
                                             │
                                         HTTPS / WSS
                                             │
                                             ▼
                                    Render / Koyeb PaaS
                              (https://pantrypilot-backend-kd0u.onrender.com)
                                             │
      ┌──────────────────────┬───────────────┴───────────────┬──────────────────────┐
      │                      │                               │                      │
      ▼                      ▼                               ▼                      ▼
Neon PostgreSQL       Upstash Cloud Redis             Supabase Cloud Storage     Google Gemini AI
(Serverless DB)     (TLS Cache & Pub/Sub)            (S3 Object Storage)      (Vision & Agent)
                             │
                             ▼
                 Render Background Worker
                  (Celery Task Runner)
