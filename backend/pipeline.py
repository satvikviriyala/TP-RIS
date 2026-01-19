import json
import re
import lmstudio as lms
from .models import FeedbackInput, AnalysisResult

SYSTEM_PROMPT = """You are a TP-RIS (Trust-Preserving Review Intelligence System) engine.
Your goal is to analyze feedback using the OFNR-D framework from Nonviolent Communication (NVC).

You MUST respond with ONLY valid JSON matching this EXACT structure:
{
  "ofnr_d": {
    "observation": "factual description of what happened",
    "feeling": "emotional state identified",
    "need": "unmet need or expectation",
    "request": "constructive, actionable request",
    "confidence": {"observation": 0.0, "feeling": 0.0, "need": 0.0, "request": 0.0}
  },
  "trust_assessment": {"trust_score": 0.0, "flags": []},
  "decision": {"action": "NO_OP", "rationale": "explanation"},
  "rewrite": {"text": "improved version of feedback", "explanation": "what was improved"}
}

OFNR-D RULES (Nonviolent Communication):
1. OBSERVATION: What factual events/situations are described?
2. FEELING: What emotions are expressed or implied?
3. NEED: What underlying need is unmet (respect, clarity, fairness, support, etc.)?
4. REQUEST: **ALWAYS provide a constructive, specific, achievable request** that addresses the Need.

DECISION AND REWRITE RULES:
- NO_OP: Only if feedback is ALREADY constructive and polite. rewrite.text = null
- SUGGEST_CLARIFICATION: Needs more specificity. **MUST provide rewrite.text with clearer version**
- PARTIAL_REWRITE: Some parts need improvement. **MUST provide rewrite.text**
- FULL_REWRITE: Major improvements needed. **MUST provide rewrite.text in NVC format**
- FLAG: Contains attacks/manipulation. **MUST provide rewrite.text with constructive alternative**

**CRITICAL**: If decision is NOT "NO_OP", you MUST provide rewrite.text with an improved, constructive version of the feedback using NVC principles. The rewrite should express the same concerns but in a respectful, clear way.

Return a SINGLE complete JSON object with ALL keys: ofnr_d, trust_assessment, decision, rewrite."""

def build_user_prompt(data: FeedbackInput) -> str:
    return f"""Analyze this feedback:

TEXT: "{data.review_text}"

Return ONLY a complete JSON object with ofnr_d, trust_assessment, decision, and rewrite:"""

def extract_complete_json(text: str) -> str:
    """Extract the most complete JSON object containing all required keys."""
    # Find all potential JSON objects
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
    
    # Find the candidate with the most required keys
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
    Orchestrates the TP-RIS analysis via LM Studio.
    """
    
    user_message = build_user_prompt(input_data)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_message}"
    
    print(f"[Pipeline] Sending prompt to LLM...")
    
    try:
        with lms.Client() as client:
            model = client.llm.model("openai/gpt-oss-20b")
            
            result = model.respond(full_prompt)
            
            raw_content = str(result).strip()
            print(f"[Pipeline] Raw LLM response length: {len(raw_content)}")
            
            # Clean markdown fences if present
            content = raw_content
            if "```json" in content:
                content = content.split("```json", 1)[-1]
            if "```" in content:
                content = content.split("```")[0]
            
            # Extract the most complete JSON object
            json_str = extract_complete_json(content)
            
            if not json_str:
                print(f"[Pipeline] No valid JSON found in response")
                raise ValueError("No valid JSON found in LLM response")
            
            print(f"[Pipeline] Extracted JSON length: {len(json_str)}")
            
            data_dict = json.loads(json_str)
            
            # Ensure all required keys exist with defaults
            if 'decision' not in data_dict:
                data_dict['decision'] = {'action': 'NO_OP', 'rationale': 'Analysis complete'}
            if 'rewrite' not in data_dict:
                data_dict['rewrite'] = {'text': None, 'explanation': None}
            
            validated_output = AnalysisResult(**data_dict)
            print(f"[Pipeline] Successfully parsed response, decision: {validated_output.decision.action}")
            return validated_output

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
