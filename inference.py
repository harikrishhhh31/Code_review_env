import asyncio
import os
import json
import textwrap
from typing import Dict, Any, Optional, List

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: OpenAI package not installed")
    exit(1)

# Import the CLIENT to interact over http/docker, not the local backend classes!
from client import CodeReviewEnvFactory
from models import CodeReviewAction

# --- CONFIGURATION VARIABLES REQUIRED BY HACKATHON ---
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
API_KEY = os.getenv("HF_TOKEN") or os.environ.get("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
BENCHMARK = "code_review_env"

MAX_STEPS = 5

SYSTEM_PROMPT = """You are an expert code reviewer. Your job is to:
1. Analyze code for issues
2. Identify bugs, security problems, and readability issues
3. Provide structured feedback.

Be specific and format your response in two parts:
1. SUMMARY: A brief overview
2. FINDINGS: List of issues.
For each finding, list:
- Type: (readability/logic/security)
- Severity: (low/medium/high/critical)
- Location: (line numbers or function name)
- Description: (what's wrong)
- Suggestion: (how to fix it)"""


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def ReviewAgent_parse(review_text: str) -> List[Dict[str, Any]]:
    findings = []
    lines = review_text.split("\n")
    current_finding = None
    
    def extract_val(l, field):
        idx = l.lower().find(field + ":")
        if idx == -1: return ""
        val = l[idx + len(field) + 1:].strip()
        for prefix in ["**", "*", "-", " "]:
            if val.startswith(prefix): val = val[1:].strip()
        return val

    for line in lines:
        line_str = line.strip().lower()
        if "type:" in line_str:
            if current_finding:
                findings.append(current_finding)
            current_finding = {
                "type": extract_val(line, "type"),
                "severity": "medium",
                "location": "unspecified",
                "description": "",
                "suggestion": ""
            }
        elif "severity:" in line_str and current_finding:
            current_finding["severity"] = extract_val(line, "severity")
        elif "location:" in line_str and current_finding:
            current_finding["location"] = extract_val(line, "location")
        elif ("description:" in line_str or "what's wrong:" in line_str) and current_finding:
            current_finding["description"] = extract_val(line, "description")
        elif ("suggestion:" in line_str or "fix:" in line_str) and current_finding:
            current_finding["suggestion"] = extract_val(line, "suggestion")
    
    if current_finding:
        findings.append(current_finding)
        
    if not findings:
        for line in lines:
            if "bug" in line.lower() or "issue" in line.lower():
                findings.append({
                    "type": "logic",
                    "severity": "medium",
                    "location": "see code",
                    "description": line.strip(" -:*"),
                    "suggestion": ""
                })
    return findings[:10]


def get_model_message(client, pr_title, pr_description, code, language, task_type):
    focus = "comprehensively review for all issues"
    if task_type == "readability":
        focus = "focus heavily on readability and style issues"
    elif task_type == "bug_logic":
        focus = "focus on logic bugs and errors"

    user_prompt = f"""Review this Pull Request:

Title: {pr_title}
Description: {pr_description}

Code to review (language: {language}):
```{language}
{code}
```

Please {focus}."""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else "No findings generated."
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "Model connection failed"


async def run_task(client, env, task_id: str):
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    try:
        result = await env.reset(task_id=task_id)
        
        pr_title = result.observation.pr_info.get("title", "")
        pr_description = result.observation.pr_info.get("description", "")
        code = result.observation.pr_info.get("code", "")
        language = result.observation.pr_info.get("language", "")
        
        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break
                
            review_text = get_model_message(client, pr_title, pr_description, code, language, task_id)
            findings = ReviewAgent_parse(review_text)
            
            action = CodeReviewAction(
                review_text=review_text,
                findings=findings,
                confidence=0.8,
                review_category=task_id
            )
            
            result = await env.step(action)
            obs = result.observation
            
            reward = result.reward or 0.0
            done = result.done
            error = None
            
            rewards.append(reward)
            steps_taken = step
            score = obs.cumulative_score
            
            log_step(step=step, action="Submitted Code Review", reward=reward, done=done, error=error)
            
            if done:
                break

        success = score > 0.1
        
    except Exception as exc:
        log_step(step=steps_taken+1, action="Exception", reward=0.0, done=True, error=str(exc))
        print(f"[DEBUG] Runtime exception inside task {task_id}: {exc}", flush=True)
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    # We must use from_docker_image if available to test external connectivity, else fallback directly!
    if LOCAL_IMAGE_NAME:
        env = CodeReviewEnvFactory.from_docker_image(LOCAL_IMAGE_NAME)
    else:
        # Fallback to localhost if testing actively without IMAGE_NAME flag
        env = CodeReviewEnvFactory.from_docker_image("local")

    tasks = ["readability", "bug_logic", "full_review"]
    
    # Check if a specific task is requested by the env runner
    target_task = os.getenv("TASK_NAME")
    if target_task and target_task in tasks:
        await run_task(client, env, target_task)
    else:
        for task_id in tasks:
            await run_task(client, env, task_id)
            
    try:
        await env.close()
    except Exception as e:
        print(f"[DEBUG] env.close() error: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
