import os
from typing import List, Optional, Dict, Any

from openai import OpenAI

from client import CodeReviewEnvFactory
from models import CodeReviewAction

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

BENCHMARK = "code_review_env"
TASKS = ["readability", "bug_logic", "full_review"]
MAX_STEPS = 3

SYSTEM_PROMPT = (
    "You are an expert code reviewer. Identify readability, logic, and security issues. "
    "Return findings with type, severity, location, description, and suggestion."
)


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    err = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={err}",
        flush=True,
    )


def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}",
        flush=True,
    )


def parse_findings(review_text: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None

    def extract_val(line: str, field: str) -> str:
        idx = line.lower().find(field + ":")
        if idx == -1:
            return ""
        val = line[idx + len(field) + 1 :].strip()
        for prefix in ("**", "*", "-", " "):
            if val.startswith(prefix):
                val = val[1:].strip()
        return val

    for raw in review_text.splitlines():
        line = raw.strip()
        low = line.lower()
        if "type:" in low:
            if current:
                findings.append(current)
            current = {
                "type": extract_val(line, "type") or "other",
                "severity": "medium",
                "location": "unspecified",
                "description": "",
                "suggestion": "",
            }
            continue
        if not current:
            continue
        if "severity:" in low:
            current["severity"] = extract_val(line, "severity") or current["severity"]
        elif "location:" in low:
            current["location"] = extract_val(line, "location") or current["location"]
        elif "description:" in low:
            current["description"] = extract_val(line, "description") or current["description"]
        elif "suggestion:" in low:
            current["suggestion"] = extract_val(line, "suggestion") or current["suggestion"]

    if current:
        findings.append(current)

    return findings[:7]


def get_model_message(client: OpenAI, task_id: str, pr: Dict[str, Any]) -> str:
    focus = "review for issues"
    if task_id == "readability":
        focus = "focus on readability and style issues"
    elif task_id == "bug_logic":
        focus = "focus on logic bugs and edge cases"
    elif task_id == "full_review":
        focus = "focus on readability, logic bugs, and security issues"

    title = pr.get("title", "")
    desc = pr.get("description", "")
    lang = pr.get("language", "")
    code = pr.get("code", "")

    user_prompt = (
        "Review this Pull Request.\n\n"
        f"Title: {title}\n"
        f"Description: {desc}\n\n"
        f"Code (language: {lang}):\n```{lang}\n{code}\n```\n\n"
        f"Please {focus}. Provide findings."
    )

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=900,
    )
    return (completion.choices[0].message.content or "").strip()


def run_task(client: OpenAI, task_id: str) -> None:
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    rewards: List[float] = []
    steps_taken = 0
    success = False
    error: Optional[str] = None

    env = CodeReviewEnvFactory.from_docker_image(LOCAL_IMAGE_NAME or "local")

    try:
        result = env.reset(task_id=task_id)
        pr_info: Dict[str, Any] = getattr(result.observation, "pr_info", {}) or {}

        for step in range(1, MAX_STEPS + 1):
            steps_taken = step
            if result.done:
                break

            review_text = get_model_message(client, task_id, pr_info)
            findings = parse_findings(review_text)
            action = CodeReviewAction(
                review_text=review_text,
                findings=findings,
                confidence=0.8,
                review_category=task_id,
            )
            result = env.step(action)
            reward = float(result.reward or 0.0)
            done = bool(result.done)
            rewards.append(reward)
            log_step(step=step, action="submit_review", reward=reward, done=done, error=error)
            if done:
                break

        score = min(max(result.observation.cumulative_score, 0.0), 1.0)
        success = score > 0.0
    except Exception as exc:
        error = str(exc)
    finally:
        try:
            env.close()
        except Exception:
            pass
        log_end(success=success, steps=steps_taken, rewards=rewards)


def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    target_task = os.getenv("TASK_NAME")
    if target_task and target_task in TASKS:
        run_task(client, target_task)
    else:
        for task_id in TASKS:
            run_task(client, task_id)


if __name__ == "__main__":
    main()
