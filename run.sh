#!/bin/bash

# GentleGiraffe Automated Deployment Script
# This script sets up the environment, installs dependencies, builds the frontend,
# configures Nginx, and starts the backend service.

set -e

# Configuration
PROJECT_ROOT="/root/TP-RIS"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
NGINX_CONF="$PROJECT_ROOT/nginx-tp-ris.conf"
PUBLIC_IP=$(hostname -I | cut -d' ' -f1)
MODEL_NAME="gemma3:27b"

echo "🦒 Starting GentleGiraffe Deployment..."
echo "----------------------------------------"

# 1. System Dependencies
echo "[1/6] Installing system dependencies..."
# Use || true to prevent script failure if apt repositories are flaky (common in some envs)
apt-get update > /dev/null || true
apt-get install -y python3.12-venv nodejs npm nginx > /dev/null || echo "⚠️  Apt install failed or packages already installed. Continuing..."
echo "✅ System dependencies check complete."

# 2. Backend Setup
echo "[2/6] Setting up Backend..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null
echo "✅ Backend environment ready."

# 3. Frontend Setup
echo "[3/6] Building Frontend..."
cd "$FRONTEND_DIR"
npm install > /dev/null
npm run build > /dev/null
echo "✅ Frontend built successfully."

# 4. Nginx Configuration
echo "[4/6] Configuring Nginx..."
mkdir -p /var/www/tp-ris
cp -r dist/* /var/www/tp-ris/
chmod -R 755 /var/www/tp-ris

# Ensure nginx config has correct IP
if [ ! -f "$NGINX_CONF" ]; then
    echo "Creating Nginx configuration..."
    cat > "$NGINX_CONF" <<EOF
server {
    listen 80;
    server_name $PUBLIC_IP;

    root /var/www/tp-ris;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
}
EOF
fi

cp "$NGINX_CONF" /etc/nginx/sites-available/tp-ris
ln -sf /etc/nginx/sites-available/tp-ris /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t > /dev/null
nginx -s reload
echo "✅ Nginx configured and reloaded."

# 5. Model Check
echo "[5/6] Checking AI Model..."
if ! ollama list | grep -q "$MODEL_NAME"; then
    echo "⚠️ Model $MODEL_NAME not found. Pulling now (this may take a while)..."
    ollama pull "$MODEL_NAME"
else
    echo "✅ Model $MODEL_NAME is available."
fi

# 6. Start Backend
echo "[6/6] Starting Backend Service..."
# Kill existing backend if running
fuser -k 8000/tcp 2>/dev/null || true
cd "$BACKEND_DIR"
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &

echo "Waiting for backend to verify health..."
sleep 5
if curl -s http://127.0.0.1:8000/health | grep -q "ok"; then
    echo "✅ Backend started successfully."
else
    echo "⚠️ Backend started but health check failed. Check /tmp/backend.log for details."
fi

echo "----------------------------------------"
echo "🎉 Deployment Complete!"
echo ""
echo "🌍 Access the application at: http://$PUBLIC_IP/"
echo ""
