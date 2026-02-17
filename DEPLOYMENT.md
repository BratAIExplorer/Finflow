# 🚀 Deployment Guide: VPS with Docker

This guide explains how to host FinFlow on any VPS (DigitalOcean, AWS, Linode, Hostinger, etc.) using Docker.

## 📋 Prerequisites
1.  **VPS Server**: Ubuntu 22.04 LTS (Recommended) with at least 2GB RAM.
2.  **Domain Name** (Optional but recommended).
3.  **Git Repository**: GitHub/GitLab (Private).

---

## 🔄 The Workflow

1.  **Local (You & Me)**: We build code here -> You commit to Git.
2.  **GitHub**: Stores the source of truth.
3.  **VPS**: Pulls code from GitHub -> Runs Docker containers.

---

## Step 1: Set Up Git (Local)

Since I (the AI) am writing files to your local machine, you need to push them to a repository.

1.  **Initialize Git**:
    ```bash
    cd c:\Antigravity\FinFlow
    git init
    git add .
    git commit -m "Initial commit - Phase 1 Foundation"
    ```

2.  **Create Repo on GitHub**:
    - Go to GitHub -> New Repository -> "FinFlow" (Private).

3.  **Link & Push**:
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/FinFlow.git
    git branch -M main
    git push -u origin main
    ```

---

## Step 2: Set Up VPS (One-Time)

SSH into your VPS:
```bash
ssh root@your_vps_ip
```

1.  **Install Docker & Compose**:
    ```bash
    apt update && apt upgrade -y
    apt install docker.io docker-compose -y
    systemctl enable --now docker
    ```

2.  **Generate SSH Key (for GitHub)**:
    ```bash
    ssh-keygen -t ed25519 -C "vps@finflow"
    cat ~/.ssh/id_ed25519.pub
    ```
    - Copy this key and add it to valid **GitHub Repo -> Settings -> Deploy Keys**.

3.  **Clone Repo**:
    ```bash
    cd /opt
    git clone git@github.com:YOUR_USERNAME/FinFlow.git
    cd FinFlow
    ```

---

## Step 3: Configure Environment

Create the `.env` file on the VPS (DO NOT commit this file to Git):

```bash
nano .env
```

Paste your production secrets:
```ini
POSTGRES_USER=finflow_secure_user
POSTGRES_PASSWORD=EXTREMELY_COMPLEX_PASSWORD_HERE
POSTGRES_DB=finflow_prod
DATABASE_URL=postgresql://finflow_secure_user:EXTREMELY_COMPLEX_PASSWORD_HERE@db:5432/finflow_prod
REDIS_URL=redis://redis:6379/0
SECRET_KEY=GENERATE_A_LONG_RANDOM_STRING_HERE
EXCHANGERATE_API_KEY=your_real_api_key
```

---

## Step 4: Run It! 🚀

Start the application:
```bash
docker-compose up -d --build
```

- **Backend**: `http://your_vps_ip:8000`
- **Docs**: `http://your_vps_ip:8000/docs`

---

## 🔄 How to Update

When we add new features (Phase 2, 3, etc.):

1.  **Local**: You pull my changes, commit, and push.
2.  **VPS**:
    ```bash
    cd /opt/FinFlow
    git pull
    docker-compose up -d --build
    ```
