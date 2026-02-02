#  GentleGiraffe - Academic Feedback Assistant

> **Pilot Project Notice**: This project has been launched as a **pilot initiative** to collect constructive feedback from students during mid-semester examinations. We are actively seeking student input to evaluate the system's effectiveness in helping craft professional, actionable academic feedback.

---

##  Overview

**GentleGiraffe** (formerly TP-RIS: Trust-Preserving Review Intelligence System) is an AI-powered academic feedback assistant designed to help students and educators provide constructive, professional, and actionable feedback in academic settings.

The system analyzes user-written feedback in real-time and provides intelligent suggestions to improve clarity, professionalism, and actionability—ensuring that feedback is both respectful and effective.

---

##  Purpose

The primary goal of GentleGiraffe is to:

1. **Transform Feedback Culture**: Help students learn how to provide constructive criticism that benefits both the giver and receiver
2. **Improve Communication Quality**: Ensure feedback is specific, professional, and actionable
3. **Collect Pilot Data**: Gather real-world usage data to refine and improve the feedback assistance algorithms
4. **Support Academic Excellence**: Enable better peer-review processes and instructor feedback

---

##  Key Features

### 1. Real-Time Feedback Analysis
- Automatically analyzes feedback text once it exceeds 80 characters
- Provides instant suggestions without interrupting the writing flow
- Live status indicator shows analysis progress (Idle → Analyzing → Ready)

### 2. Intelligent Decision System
The AI classifies feedback into five categories:

| Action | Description |
|--------|-------------|
| **NO_OP** | Feedback is already constructive and professional—no changes needed ✓ |
| **SUGGEST_CLARIFICATION** | Feedback is vague—provides guiding questions to add specificity |
| **PARTIAL_REWRITE** | Good points exist but tone/phrasing needs improvement |
| **FULL_REWRITE** | Complete rewrite needed due to unprofessional or aggressive tone |
| **FLAG** | Content flagged for abusive, inappropriate, or incoherent input |

### 3. Suggested Rewrites
- When feedback needs improvement, the system provides professionally rewritten alternatives
- Users can **Accept** the suggested rewrite (auto-populates the editor) or **Dismiss** it
- Explanations accompany each suggestion to help users understand the improvement

### 4. Visual Feedback Indicators
- **Green Badge (NO_OP)**: Your feedback is good to go!
- **Yellow Badge (CLARIFICATION)**: Consider adding more details
- **Purple Badge (REWRITE)**: A suggestion is available
- **Red Badge (FLAG)**: Content needs attention

### 5. Submit Gate Logic
- The "Submit Feedback" button is only enabled when:
  - The analysis determines feedback is acceptable (NO_OP), OR
  - The user accepts a suggested rewrite
- This ensures only constructive feedback is submitted

### 6. Character Counter
- Visual indicator showing current character count vs. minimum threshold (80 chars)
- Turns green when the threshold is met

---

##  Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GentleGiraffe                           │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript + Vite)                       │
│  ├── Editor Component (Text input with live analysis)       │
│  ├── SuggestionPanel (Displays AI recommendations)          │
│  └── StatusIndicator (Shows analysis state)                 │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + Python)                                 │
│  ├── REST API (/analyze-feedback endpoint)                  │
│  ├── Pipeline (OFNR-D analysis framework)                   │
│  └── Ollama Integration (Local LLM inference)               │
├─────────────────────────────────────────────────────────────┤
│  AI Engine (Ollama + LLM)                                   │
│  └── Model: gpt-oss:20b or gemma3:27b                       │
└─────────────────────────────────────────────────────────────┘
```

---

##  Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Ollama** (for local LLM inference)

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/satvikviriyala/TP-RIS.git
cd TP-RIS
```

#### 2. Setup Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Setup Frontend
```bash
cd ../frontend
npm install
```

#### 4. Install Ollama & Pull Model
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the required model
ollama pull gemma3:27b
```

### Running the Application

#### Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### Start Frontend (Development)
```bash
cd frontend
npm run dev
```

#### Access the Application
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

##  Configuration

### Changing the AI Model

Edit `backend/pipeline.py`:
```python
MODEL_NAME = "gemma3:27b"  # or "gpt-oss:20b", "qwen3:235b", etc.
```

### Adjusting Analysis Behavior

- **System Prompt**: Modify `SYSTEM_PROMPT` in `backend/pipeline.py` to change tone/rules
- **Temperature**: Adjust the `temperature` setting (0.0 = strict, 1.0 = creative)
- **Minimum Characters**: Change the threshold in `frontend/src/components/Editor.tsx`

---

##  Project Structure

```
TP-RIS/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── pipeline.py          # AI analysis pipeline with Ollama
│   ├── models.py            # Pydantic data models
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main application component
│   │   ├── components/
│   │   │   ├── Editor.tsx         # Feedback editor with live analysis
│   │   │   ├── SuggestionPanel.tsx # AI suggestion display
│   │   │   └── StatusIndicator.tsx # Analysis status indicator
│   │   └── hooks/
│   │       └── useAnalysis.ts     # Custom hook for API integration
│   └── package.json         # Node.js dependencies
├── running_guide.md         # Detailed deployment guide
├── run.sh                   # Automated deployment script
└── README.md                # This file
```

---

##  How to Use (For Students)

1. **Open the Application**: Navigate to the provided URL
2. **Write Your Feedback**: Type your feedback in the editor (minimum 80 characters)
3. **Wait for Analysis**: The system will automatically analyze your feedback
4. **Review Suggestions**: If suggestions appear, read the rationale
5. **Accept or Dismiss**: Either accept the rewrite or dismiss to keep your original
6. **Submit**: Click "Submit Feedback" when the button turns green

### Tips for Good Feedback
- Be specific about what needs improvement
- Focus on the work, not the person
- Suggest concrete actions when possible
- Maintain a professional and respectful tone

---

##  Pilot Program Information

### Goals
- Evaluate the effectiveness of AI-assisted feedback improvement
- Gather user experience data to refine the system
- Measure improvement in feedback quality over time

### Feedback Collection
All submitted feedback is logged for analysis purposes. No personal identifying information is collected.

### Participation
Your participation in this pilot helps us improve academic communication tools. If you have suggestions or encounter issues, please report them through the designated channels.

---

##  Troubleshooting

| Issue | Solution |
|-------|----------|
| "502 Bad Gateway" | Backend isn't running. Start with `uvicorn main:app --reload` |
| "AI Response is Empty" | Ensure Ollama is running: `systemctl status ollama` |
| Analysis not triggering | Make sure you've typed at least 80 characters |
| Suggestions not appearing | Check browser console for API errors |

---

##  Credits

**Developed by**: ScaDS AI Lab  
**Project Lead**: Satvik Viriyala

---

##  License

This project is developed for academic research purposes at Leipzig University.

---

<p align="center">
  Made with ❤️ for better academic communication
</p>
