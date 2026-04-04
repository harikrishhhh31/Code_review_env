---
title: CodeReviewEnv
emoji: 📝
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# CodeReviewEnv - AI-Powered Code Review Environment

![OpenEnv](https://img.shields.io/badge/OpenEnv-Environment-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**CodeReviewEnv** is a reinforcement learning environment for training AI agents to perform code review tasks. Agents learn to analyze pull requests, identify bugs, security vulnerabilities, and readability issues.

## Overview

CodeReviewEnv simulates a professional code review workflow where an AI agent:

1. **Receives** a Pull Request with code to review
2. **Analyzes** the code for various issues
3. **Submits** findings as structured feedback
4. **Receives** rewards based on accuracy

Task samples include **Python**, **JavaScript**, and **TypeScript** to encourage multi-language review skills.

## Quick Start

### Python Library (Local Development)

```python
from server.code_review_env import CodeReviewEnvironment
from models import CodeReviewAction

# Create environment
env = CodeReviewEnvironment()

# Reset to get initial observation
obs = env.reset(task_id="readability")

print(f"PR to review: {obs.pr_info['title']}")
print(f"Code:\n{obs.pr_info['code']}")

# Submit code review
action = CodeReviewAction(
    review_text="Found readability issues...",
    findings=[
        {
            "type": "readability",
            "severity": "medium",
            "location": "function calc",
            "description": "Function name is vague",
            "suggestion": "Rename to calculate_sum"
        }
    ]
)

# Get feedback and reward
result = env.step(action)

print(f"Score: {result.cumulative_score}")
print(f"Feedback: {result.feedback}")

# Clean up
env.close()
```

### Run Baseline Inference (Optional)

```bash
# Set OpenAI API key (required only for baseline script)
export OPENAI_API_KEY=sk-...

# Run baseline on all tasks
python inference.py

# Run on specific task
python inference.py --task readability --verbose
```

Baseline inference is optional and does not affect environment validation or deployment.

## Tasks

### Task 1: Readability Review (Easy)

**Objective:** Identify code style and readability issues.

**What to find:**
- Poor variable/function names
- Missing documentation
- Missing type hints
- Complex logic

### Task 2: Bug & Logic Review (Medium)

**Objective:** Find logic errors and bugs in code.

**What to find:**
- Off-by-one errors
- Missing edge case handling
- Incorrect algorithms
- Empty list handling

### Task 3: Full PR Review (Hard)

**Objective:** Complete code review including security analysis.

**What to find:**
- All readability issues
- All logic bugs
- Security vulnerabilities (SQL injection, XSS, etc.)
- PR description accuracy

## Scoring

| Task | Difficulty | Description |
|------|------------|-------------|
| Readability Review | Easy | Identify code style and clarity issues |
| Bug & Logic Review | Medium | Find logic errors and bugs |
| Full PR Review | Hard | Complete review with security analysis |

## Reward Design

CodeReviewEnv uses **dense rewards** (feedback at each step) rather than sparse rewards.

| Component | Weight | Description |
|-----------|--------|-------------|
| Correct finding | 0.1-0.3 | Points for each true positive |
| False positive | -0.1 | Penalty for incorrect finding |
| Completeness bonus | 0.2 | Bonus for finding all issues |
| Final score | 0.0-1.0 | Normalized total |

## Environment API

| Method | Description |
|--------|-------------|
| `reset(task_id, task_index)` | Start new episode, returns initial observation |
| `step(action)` | Take action, returns observation with reward |
| `state` | Get current internal state (property) |

## Installation

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/code-review-env.git
cd code-review-env

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Using Docker

```bash
# Build the container
docker build -t code-review-env:latest -f server/Dockerfile .

# Run the container
docker run -p 8000:8000 code-review-env:latest
```

## Project Structure

```
code_review_env/
|-- __init__.py
|-- models.py
|-- rubric.py
|-- server/
|   |-- app.py
|   |-- code_review_env.py
|   |-- Dockerfile
|   |-- tasks/
|       |-- task_data.py
|-- inference.py
|-- openenv.yaml
|-- README.md
```

## Deployment

### Deploy to Hugging Face Spaces

```bash
# Login to Hugging Face
huggingface-cli login

# Push to Hub
openenv push --repo-id your-username/code-review-env
```

## Development Status

**Current Phase:** Initial implementation with 3 tasks

**Planned Enhancements:**
- [ ] Expand task pool (more PR samples)
- [ ] Add multi-language support (JavaScript, Java, Go)
- [ ] Improve grader precision
- [ ] Add multi-step investigation actions
- [ ] Security vulnerability detection enhancements

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
