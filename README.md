# CodeReviewEnv

A reinforcement learning environment for training AI agents to perform code review tasks.

## Overview

CodeReviewEnv simulates a professional code review workflow where an AI agent:
1. Receives a Pull Request with code to review
2. Analyzes the code for various issues (bugs, security, readability)
3. Submits findings as structured feedback
4. Receives rewards based on accuracy

## Quick Start

```python
from server.code_review_env import CodeReviewEnvironment
from models import CodeReviewAction

# Create environment
env = CodeReviewEnvironment()

# Reset to get initial observation
obs = env.reset(task_id="readability")
print(f"PR to review: {obs.pr_info['title']}")

# Submit code review
action = CodeReviewAction(
    review_text="Found readability issues...",
    findings=[{"type": "readability", "severity": "medium", ...}]
)

# Get feedback and reward
result = env.step(action)
print(f"Reward: {result.reward}")
```

## Project Structure

```
code_review_env/
├── models.py              # Typed models (Action, Observation, State)
├── rubric.py             # Grading rubrics
├── server/
│   ├── app.py           # FastAPI server
│   ├── code_review_env.py  # Core environment
│   └── tasks/
│       └── task_data.py   # PR samples
```

## Tasks

| Task | Description |
|------|-------------|
| readability | Find code style and clarity issues |
| bug_logic | Find logic errors and bugs |
| full_review | Complete review including security |

## License

MIT