# 🚀 FinFlow VPS Production Deployment Guide

This guide details how to deploy and maintain FinFlow on any Linux VPS (Ubuntu 22.04 / 24.04 LTS recommended on Hostinger, DigitalOcean, AWS, Linode, Hetzner, etc.) using Docker and Docker Compose.

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
