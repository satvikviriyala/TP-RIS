# 🦒 GentleGiraffe Deployment Guide

Welcome to **GentleGiraffe** (formerly TP-RIS). This guide provides everything you need to deploy, run, and manage the application.

## 🚀 Quick Start (Automated)

The easiest way to get running is using the included **Automation Script**.

### 1. Run the Auto-Deploy Script
This script handles dependency installation, building, config, and startup automatically.

```bash
# Make the script executable
chmod +x run.sh

# Run the deployment
./run.sh
```

**What this does:**
1. Installs system tools (`python3`, `node`, `npm`, `nginx`).
2. Creates a clean Python virtual environment.
3. Installs backend dependencies (`fastapi`, `uvicorn`, etc.).
4. Builds the React frontend for production.
5. Configures and reloads Nginx.
6. Ensures the AI model (`gemma3:27b`) is pulled.
7. Restart the backend service.

---

## 🛠️ Manual Deployment

If you prefer to set things up step-by-step, follow these instructions.

### Prerequisites
- **OS**: Linux (Ubuntu/Debian recommended)
- **Ollama**: Installed and running (`curl -fsSL https://ollama.com/install.sh | sh`)
- **Ports**: Ensure ports `80` (HTTP) and `8000` (Backend) are free.

### Phase 1: Backend (Python)

1. **Navigate to the backend:**
   ```bash
   cd backend
   ```

2. **Setup Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start the Service:**
   ```bash
   # Run in background
   nohup uvicorn main:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
   ```

### Phase 2: Frontend (React)

1. **Navigate to the frontend:**
   ```bash
   cd ../frontend
   ```

2. **Build the Application:**
   ```bash
   npm install
   npm run build
   ```
   *This creates a `dist/` folder with the optimized website.*

### Phase 3: Web Server (Nginx)

1. **Deploy Files:**
   ```bash
   sudo mkdir -p /var/www/tp-ris
   sudo cp -r dist/* /var/www/tp-ris/
   ```

2. **Configure Nginx:**
   Copy the `nginx-tp-ris.conf` to `/etc/nginx/sites-available/` and link it.
   ```bash
   sudo ln -sf /etc/nginx/sites-available/tp-ris /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

---

## 🔧 Configuration

### changing the AI Model
To change the model (e.g., to `gpt-oss:120b` or `qwen3:235b`):
1. Edit `backend/pipeline.py`:
   ```python
   MODEL_NAME = "gpt-oss:120b"
   ```
2. Edit `run.sh`:
   ```bash
   MODEL_NAME="gpt-oss:120b"
   ```
3. Run `./run.sh` again to apply changes.

### Tuning Behavior
- **System Prompt**: Edit `backend/pipeline.py` to change the tone or rules.
- **Temperature**: Adjust the `temperature` setting in `backend/pipeline.py` (0.0 = strict, 1.0 = creative).

---

## ❓ Troubleshooting

**"502 Bad Gateway"**
- The backend isn't running. Check logs: `tail -f /tmp/backend.log`
- Ensure no other service is using port 8000.

**"AI Response is Empty"**
- Check if Ollama is running: `systemctl status ollama`
- Verify model exists: `ollama list`

**"Permission Denied"**
- Ensure you used `chmod +x run.sh`.
- Run commands with `sudo` if modifying system files manually.
