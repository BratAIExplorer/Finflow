# 🚀 FinFlow VPS Production Deployment Guide

This guide details how to deploy and maintain FinFlow on any Linux VPS (Ubuntu 22.04 / 24.04 LTS recommended on Hostinger, DigitalOcean, AWS, Linode, Hetzner, etc.) using Docker and Docker Compose.

> **Status: already deployed, with HTTPS.** Live at `https://finflow.fortressintelligence.space` (Hostinger VPS `76.13.179.32`, nginx reverse proxy + free Let's Encrypt cert, auto-renews). Security-audited — see `CURRENT_STATUS.md` for the live URL, what was fixed, and the full audit. The steps below are the general playbook and don't match exactly how this instance was actually set up:
> - Code was copied with `scp`/`tar` directly to `/opt/FinFlow`, not `git clone` — no GitHub deploy key was set up on the VPS. **This is a known gap — see "Note on the current VPS deploy" below.**
> - Ports are remapped to 8001 (API) / 3001 (app) internally — the VPS already runs other apps on 8000/3000/5432 — but neither is meant to be hit directly anymore; nginx on 80/443 is the front door.
> - Postgres and Redis have no host port at all (container-internal only).
> - To redeploy after a code change: `scp` the changed file(s) to `/opt/FinFlow/...` on the VPS, then `ssh root@76.13.179.32 "cd /opt/FinFlow && docker compose up -d --build <service>"` (`backend`, `frontend`, or omit the service name to rebuild everything).

## 📋 Prerequisites
1.  **VPS Server**: Ubuntu 22.04 LTS (Recommended) with at least 2GB RAM.
2.  **Domain Name** (Optional but recommended).
3.  **Git Repository**: GitHub/GitLab (Private).

---

## 📋 System Requirements

- **OS**: Ubuntu 22.04 LTS / 24.04 LTS
- **RAM**: 2GB minimum (4GB recommended for Docker builds)
- **Disk**: 15GB+ SSD storage
- **Ports**: 80 (HTTP), 443 (HTTPS), 3000 (Frontend), 8000 (Backend API)

---

## ⚡ Quick Deployment (Automated)

### 1. SSH into your VPS
```bash
ssh root@YOUR_VPS_IP
```

### 2. Install Docker & Git (if not already installed)
```bash
apt update && apt upgrade -y
apt install -y docker.io docker-compose git curl
systemctl enable --now docker
```

### 3. Clone the Repository
```bash
git clone https://github.com/BratAIExplorer/Finflow.git /opt/Finflow
cd /opt/Finflow
```

### 4. Configure Environment
```bash
cp .env.example .env
nano .env
```
*Customize your PostgreSQL password, database name, and secret keys.*

Paste your production secrets:
```ini
POSTGRES_USER=finflow_secure_user
POSTGRES_PASSWORD=EXTREMELY_COMPLEX_PASSWORD_HERE
POSTGRES_DB=finflow_prod
DATABASE_URL=postgresql://finflow_secure_user:EXTREMELY_COMPLEX_PASSWORD_HERE@db:5432/finflow_prod
REDIS_URL=redis://redis:6379/0
SECRET_KEY=GENERATE_A_LONG_RANDOM_STRING_HERE
APP_ENCRYPTION_KEY=GENERATE_WITH_Fernet.generate_key()
EXCHANGERATE_API_KEY=your_real_api_key
```
`APP_ENCRYPTION_KEY` encrypts broker credentials at rest — without it, `/holdings/accounts` throws on every request. Generate one: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.

---

### 5. Launch Application
```bash
chmod +x deploy.sh
./deploy.sh
```

FinFlow will build and launch:
- **Frontend (Light & Dark UI)**: `http://YOUR_VPS_IP:3000`
- **Backend API**: `http://YOUR_VPS_IP:8000`
- **API Swagger Documentation**: `http://YOUR_VPS_IP:8000/docs`

---

## 🔄 Routine Updates & Redeployment

Whenever updates are pushed to the GitHub repository (`https://github.com/BratAIExplorer/Finflow`), updating your VPS is as simple as:

```bash
cd /opt/Finflow
./deploy.sh
```

The script automatically:
1. Pulls the latest commits from `origin/main`.
2. Rebuilds updated container images using Next.js standalone optimization and Python caching.
3. Restarts the containers with zero downtime.

---

## 🔒 Optional: Domain & SSL Setup (Nginx + Certbot)

To access your FinFlow dashboard via a secure custom domain (e.g., `https://finflow.yourdomain.com`):

### 1. Install Nginx & Certbot
```bash
apt install -y nginx certbot python3-certbot-nginx
```

### 2. Create Nginx Site Configuration
```bash
nano /etc/nginx/sites-available/finflow
```

Add the following configuration:
```nginx
server {
    server_name finflow.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Enable Site & Generate Free SSL Certificate
```bash
ln -s /etc/nginx/sites-available/finflow /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

certbot --nginx -d finflow.yourdomain.com
```

---

## 🛠️ Maintenance & Troubleshooting

### View Container Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f db
```

### Restart Services
```bash
docker-compose restart
```

### Database Backup & Restore
```bash
# Backup
docker exec -t finflow-db pg_dump -U finflow_user finflow_prod > backup_$(date +%F).sql

# Restore
cat backup_2026-09-14.sql | docker exec -i finflow-db psql -U finflow_user -d finflow_prod
```
