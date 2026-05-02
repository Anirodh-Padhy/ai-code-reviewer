import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"


# ================= AI REVIEW =================
def review_code_with_ai(code, language):

    prompt = f"""
You are an expert {language} developer.

Analyze the following {language} code and return STRICTLY in this format:

Score: X/10

Bugs:
- ...

Code Smells:
- ...

Best Practices:
- ...

Suggestions:
- ...

Code:
{code}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        result = response.json().get("response", "")

        return format_ai_output(result)

    except Exception as e:
        return {"score": "N/A", "raw": f"AI Error: {str(e)}"}


# ================= FORMAT OUTPUT =================
def format_ai_output(text):

    score_match = re.search(r"Score:\s*(\d+)/10", text)
    score = score_match.group(1) if score_match else "N/A"

    return {
        "score": score,
        "raw": text
    }
    
def improve_code_with_ai(code, language):

    import random

    variations = [
        "Keep it minimal and simple",
        "Focus on readability",
        "Focus on clean structure",
        "Keep beginner-friendly style"
    ]

    style = random.choice(variations)

    prompt = f"""
You are an expert {language} developer.

Improve the following code with STRICT RULES:

- DO NOT change core logic
- DO NOT over-engineer
- {style}

Return ONLY improved code.

Code:
{code}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json().get("response", "")

    except Exception as e:
        return f"AI Error: {str(e)}"