import json
import requests
from .models import FeedbackInput, AnalysisResult

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gpt-oss:20b"

SYSTEM_PROMPT = """You are an expert Academic Review Assistant. Your role is to help users provide constructive, professional, and actionable feedback in an academic or professional setting.

Your internal analysis engine uses the OFNR-D framework (Observation, Feeling, Need, Request), but you must NEVER mention these terms or the framework itself to the user. Your output must feel completely natural, like a helpful senior colleague suggesting an edit.

INTERNALLY Analyze the input:
1. Is it based on facts/observations? (vs judgments/insults) is it coherent?
2. What is the emotional tone?
3. What is the core need (clarity, rigor, novelty, citation, etc.)?
4. Is there a clear request?

OUTPUT FORMAT:
You must respond with valid JSON structure:
{
  "ofnr_d": {
    "observation": "internal note", "feeling": "internal note", "need": "internal note", "request": "internal note",
    "confidence": {"observation": 1.0, "feeling": 1.0, "need": 1.0, "request": 1.0}
  },
  "trust_assessment": {"trust_score": 0.0, "flags": []},
  "decision": {"action": "ACTION_TYPE", "rationale": "Natural explanation of why"},
  "rewrite": {"text": "See specific rules below", "explanation": "Brief note on improvement"}
}

DECISION LOGIC & REWRITE RULES:

1. **NO_OP** (Feedback is good):
   - Use this if feedback is constructive, specific, and polite.
   - `rewrite.text`: null

2. **SUGGEST_CLARIFICATION** (Vague/Ambiguous):
   - Use this if the feedback says "it's bad" or "fix this" without saying *why* or *how*.
   - **CRITICAL**: Do NOT write the full feedback for them.
   - `rewrite.text`: Provide 2-3 short questions or hints to help them clarify. Example: "Consider specifying which section needs more references." or "Could you give an example of the 'confusing logic'?"
   - `rationale`: "This feedback is a bit vague. Specifics help the author improve."

3. **PARTIAL_REWRITE** (Good points, but tone/phrasing issues):
   - Use this if valid points exist but are buried in frustration or casual language.
   - `rewrite.text`: specific, professional academic phrasing of the user's intent.
   - NO NVC jargon.

4. **FULL_REWRITE** (Aggressive/Unprofessional/Incoherent):
   - Use this for insults, ranting, or non-academic tone.
   - `rewrite.text`: A completely professional, constructive version addressing the core issue.

5. **FLAG** (Abusive/Hate Speech/Gibberish):
   - Use this for completely unacceptable content.
   - `rewrite.text`: A neutral, professional alternative if possible, or null if gibberish.

TONE & STYLE GUIDE:
- **Balanced Professionalism**: The tone should be strictly professional and constructive.
- **Not Overly Friendly**: Avoid "coworker" vibes or excessive politeness like "I feel" or "Maybe you could". 
- **Not Harsh**: Avoid aggressive language. Be direct but neutral.
- **Objective**: Focus strictly on the work/content, not the person.
- **No Leaking**: NEVER use words: OFNR, NVC, Nonviolent, Observation, Feeling, Need, Request.
- **No Gibberish**: If input is random characters, return NO_OP or FLAG.

Return ONLY the JSON object."""

def build_user_prompt(data: FeedbackInput) -> str:
    return f"""Analyze this feedback:

TEXT: "{data.review_text}"

Return ONLY a complete JSON object with ofnr_d, trust_assessment, decision, and rewrite:"""

def extract_complete_json(text: str) -> str:
    """Extract the most complete JSON object containing all required keys."""
    candidates = []
    start = 0
    
    while True:
        start_idx = text.find('{', start)
        if start_idx == -1:
            break
            
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i, char in enumerate(text[start_idx:], start_idx):
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    candidate = text[start_idx:i+1]
                    candidates.append(candidate)
                    break
        
        start = start_idx + 1
    
    required_keys = ['ofnr_d', 'trust_assessment', 'decision', 'rewrite']
    best_candidate = ""
    best_score = 0
    
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                score = sum(1 for key in required_keys if key in parsed)
                if score > best_score:
                    best_score = score
                    best_candidate = candidate
        except:
            continue
    
    return best_candidate

def analyze_with_llm(input_data: FeedbackInput) -> AnalysisResult:
    """
    Orchestrates the TP-RIS analysis via Ollama.
    """
    
    user_message = build_user_prompt(input_data)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_message}"
    
    print(f"[Pipeline] Sending prompt to Ollama ({MODEL_NAME})...")
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5
                }
            },
            timeout=120
        )
        response.raise_for_status()
        
        result_data = response.json()
        raw_content = result_data.get("response", "").strip()
        print(f"[Pipeline] Raw LLM response length: {len(raw_content)}")
        
        # Clean markdown fences if present
        content = raw_content
        if "```json" in content:
            content = content.split("```json", 1)[-1]
        if "```" in content:
            content = content.split("```")[0]
        
        json_str = extract_complete_json(content)
        
        if not json_str:
            print(f"[Pipeline] No valid JSON found in response")
            raise ValueError("No valid JSON found in LLM response")
        
        print(f"[Pipeline] Extracted JSON length: {len(json_str)}")
        
        data_dict = json.loads(json_str)
        
        if 'decision' not in data_dict:
            data_dict['decision'] = {'action': 'NO_OP', 'rationale': 'Analysis complete'}
        if 'rewrite' not in data_dict:
            data_dict['rewrite'] = {'text': None, 'explanation': None}
        
        # FIX: Handle case where LLM returns a list of strings for rewrite.text
        if data_dict['rewrite'].get('text') and isinstance(data_dict['rewrite']['text'], list):
            print(f"[Pipeline] Handling list output for rewrite.text: {data_dict['rewrite']['text']}")
            data_dict['rewrite']['text'] = "\n".join(data_dict['rewrite']['text'])
        
        validated_output = AnalysisResult(**data_dict)
        print(f"[Pipeline] Successfully parsed response, decision: {validated_output.decision.action}")
        return validated_output

    except requests.exceptions.RequestException as e:
        print(f"[Pipeline] Ollama request error: {e}")
        return AnalysisResult(
            ofnr_d={
                "observation": None, "feeling": None, "need": None, "request": None,
                "confidence": {"observation": 0, "feeling": 0, "need": 0, "request": 0}
            },
            trust_assessment={"trust_score": 0.0, "flags": ["connection_error"]},
            decision={"action": "NO_OP", "rationale": f"Could not connect to Ollama: {str(e)}"},
            rewrite={"text": None, "explanation": None}
        )
    except json.JSONDecodeError as e:
        print(f"[Pipeline] JSON parse error: {e}")
        return AnalysisResult(
            ofnr_d={
                "observation": None, "feeling": None, "need": None, "request": None,
                "confidence": {"observation": 0, "feeling": 0, "need": 0, "request": 0}
            },
            trust_assessment={"trust_score": 0.0, "flags": ["json_parse_error"]},
            decision={"action": "NO_OP", "rationale": f"Failed to parse LLM response"},
            rewrite={"text": None, "explanation": None}
        )
    except Exception as e:
        print(f"[Pipeline] Error during inference: {e}")
        return AnalysisResult(
            ofnr_d={
                "observation": None, "feeling": None, "need": None, "request": None,
                "confidence": {"observation": 0, "feeling": 0, "need": 0, "request": 0}
            },
            trust_assessment={"trust_score": 0.0, "flags": ["system_error"]},
            decision={"action": "NO_OP", "rationale": f"System error: {str(e)}"},
            rewrite={"text": None, "explanation": None}
        )
