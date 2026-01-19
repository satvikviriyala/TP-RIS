# TP-RIS Offline Prototype

Trusted-Preserving Review Intelligence System (Offline Mode).

## Setup

1. **Prerequisites**
   - Python 3.10+
   - Node.js 18+
   - LM Studio (with `openai/gpt-oss-20b`)

2. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Usage
Open [http://localhost:5173](http://localhost:5173).
Ensure LM Studio server is running on port 1234.
