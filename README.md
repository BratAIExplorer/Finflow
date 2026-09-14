# 🏦 FinFlow - Personal Wealth Hub

> **A high-frequency, multi-currency personal wealth tracker designed for global portfolios.** Aggregate every asset, liability, and currency in an ultra-modern glassmorphic interface.

[![Next.js](https://img.shields.io/badge/Next.js-16.1.6-black?style=flat&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2-blue?style=flat&logo=react)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-v4-38bdf8?style=flat&logo=tailwindcss)](https://tailwindcss.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com/)

---

## ✨ Key Features

- ☀️ / 🌙 **Dual Theme Engine (Light & Dark Mode)**:
  - Instant toggle switch in the floating glass navigation bar.
  - Custom frosted glass cards adapted for both midnight dark and crisp white light mode.
  - Zero-flicker pre-hydration script with persistent `localStorage` preference.
- 🔍 **Enhanced Readability Typography**:
  - Scaled typography scale (+15–20% boost) across all components for superior legibility.
  - High-contrast text gradients, enlarged net worth metrics, and spacious touch-friendly forms.
- 🌐 **Multi-Currency First**:
  - Real-time conversion across **USD, MYR, INR, and SGD**.
  - Smart regional number formatting and live currency indicators.
- 💎 **Premium Glassmorphism Design System**:
  - Layered blur surfaces, ambient glow orbs, and micro-interactions powered by Framer Motion.
- 📈 **Visual Asset Intelligence**:
  - Interactive portfolio trajectory area charts, asset breakdowns (Crypto, Stocks, Real Estate, Cash), and manual asset intake modal.
- 🐳 **Production Docker & VPS Ready**:
  - Multi-stage Next.js standalone container, FastAPI backend, PostgreSQL 15, and Redis 7 all managed via Docker Compose.

---

## 🛠️ Architecture & Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 16 (App Router & Turbopack), React 19, TypeScript, Tailwind CSS v4, Framer Motion, Lucide Icons, Recharts |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, Uvicorn |
| **Database & Cache** | PostgreSQL 15, Redis 7 |
| **Deployment** | Docker, Docker Compose, Linux VPS (Ubuntu / Debian / Hostinger / AWS / Linode) |

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- **Node.js**: v20+ (v22 recommended)
- **Python**: 3.11+
- **Git**

### 2. Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Run Backend
```bash
# In project root
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```
API Documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## ☁️ VPS Deployment Guide

Deploying FinFlow to your VPS takes less than 2 minutes using Docker:

### 1. On your VPS:
```bash
# Clone the repository
git clone https://github.com/BratAIExplorer/Finflow.git /opt/Finflow
cd /opt/Finflow

# Configure environment variables
cp .env.example .env
nano .env

# Run automated deployment
chmod +x deploy.sh
./deploy.sh
```

### 2. Updating on VPS
Whenever you push updates to GitHub, simply run:
```bash
cd /opt/Finflow
./deploy.sh
```
The script will pull the latest code, build the standalone images, and restart services with zero orphaned containers.

---

## 📁 Repository Structure

```
Finflow/
├── backend/                  # FastAPI Python backend
│   ├── routers/              # API Route handlers (auth, assets, family)
│   ├── currency.py           # Multi-currency FX converter
│   ├── database.py           # SQLAlchemy database setup
│   └── main.py               # Application entry point
├── frontend/                 # Next.js 16 frontend
│   ├── app/
│   │   ├── globals.css       # Light/Dark tokens & Glassmorphism styles
│   │   ├── layout.tsx        # Pre-hydration theme loader
│   │   └── page.tsx          # Dashboard page with ThemeToggle
│   ├── components/
│   │   ├── ThemeToggle.tsx   # Light/Dark switch button
│   │   ├── AddAssetForm.tsx  # Manual asset intake modal
│   │   └── ui/               # Reusable glass UI components
│   ├── lib/
│   │   └── utils.ts          # Classnames utility (clsx + twMerge)
│   └── Dockerfile            # Multi-stage standalone Next.js build
├── docker-compose.yml        # Production Docker orchestration
├── deploy.sh                 # VPS one-click deployment script
├── .env.example              # Environment variables template
└── DEPLOYMENT.md             # In-depth server deployment documentation
```

---

## 📄 License
Private & Proprietary • FinFlow 2026
