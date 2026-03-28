# CodeReviewEnv - AI-Powered Code Review Environment

![OpenEnv](https://img.shields.io/badge/OpenEnv-Environment-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**CodeReviewEnv** is a reinforcement learning environment for training AI agents to perform code review tasks. Agents learn to analyze pull requests, identify bugs, security vulnerabilities, and readability issues.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Environment API](#environment-api)
- [Tasks](#tasks)
- [Reward Design](#reward-design)
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)
- [Deployment](#deployment)

## Overview

CodeReviewEnv simulates a professional code review workflow where an AI agent:

1. **Receives** a Pull Request with code to review
2. **Analyzes** the code for various issues
3. **Submits** findings as structured feedback
4. **Receives** rewards based on accuracy

The environment supports three difficulty levels:

| Task | Difficulty | Description |
|------|------------|-------------|
| Readability Review | Easy | Identify code style and clarity issues |
| Bug & Logic Review | Medium | Find logic errors and bugs |
| Full PR Review | Hard | Complete review with security analysis |

## Quick Start

### Option 1: Use as a Python Library (Local Development)

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
    review_text="Found 2 readability issues...",
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

### Option 2: Run Baseline Inference

```bash
# Set OpenAI API key
export OPENAI_API_KEY=sk-...

# Run baseline on all tasks
python baseline_inference.py

# Run on specific task
python baseline_inference.py --task readability --verbose
```

## Environment API

CodeReviewEnv follows the OpenEnv specification with typed models.

### Core Methods

| Method | Description |
|--------|-------------|
| `reset(task_id, task_index)` | Start new episode, returns initial observation |
| `step(action)` | Take action, returns observation with reward |
| `state` | Get current internal state (property) |

### Models

#### CodeReviewAction

```python
class CodeReviewAction(Action):
    review_text: str                    # Agent's review text
    findings: List[Dict[str, Any]]     # Structured issues found
    confidence: float                   # Agent confidence (0.0-1.0)
    review_category: str               # 'readability', 'bug_logic', 'full_review'
```

#### CodeReviewObservation

```python
class CodeReviewObservation(Observation):
    pr_info: Dict[str, Any]           # PR title, description, code
    feedback: str                      # Environment feedback
    score_breakdown: Dict[str, float] # Scores by category
    reward: float                      # Step reward
    cumulative_score: float            # Total episode score
    done: bool                         # Episode complete?
```

## Tasks

### Task 1: Readability Review (Easy)

**Objective:** Identify code style and readability issues.

**What to find:**
- Poor variable/function names
- Missing documentation
- Missing type hints
- Complex logic

**Example Issues:**
```python
# Bad: def calc(a,b):
# Good: def calculate_sum(first_number, second_number):
```

### Task 2: Bug & Logic Review (Medium)

**Objective:** Find logic errors and bugs in code.

**What to find:**
- Off-by-one errors
- Missing edge case handling
- Incorrect algorithms
- Empty list handling

**Example Issues:**
```python
# Bug: max_val = 0  # Fails for negative numbers
# Fix: max_val = float('-inf') or first element
```

### Task 3: Full PR Review (Hard)

**Objective:** Complete code review including security analysis.

**What to find:**
- All readability issues
- All logic bugs
- Security vulnerabilities (SQL injection, XSS, etc.)
- PR description accuracy

**Example Issues:**
```python
# Security: query = f"SELECT * FROM users WHERE name='{username}'"
# Fix: query = "SELECT * FROM users WHERE name=?", (username,)
```

## Reward Design

CodeReviewEnv uses **dense rewards** (feedback at each step) rather than sparse rewards (only at the end). This helps agents learn faster.

### Reward Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Correct finding | 0.1-0.3 | Points for each true positive |
| False positive | -0.1 | Penalty for incorrect finding |
| Completeness bonus | 0.2 | Bonus for finding all issues |
| Final score | 0.0-1.0 | Normalized total |

### Score Breakdown

The environment provides detailed scoring by category:

```python
score_breakdown = {
    "readability": 0.8,    # 80% of readability issues found
    "logic": 0.5,          # 50% of bugs found
    "security": 0.0,       # No security issues (for readability task)
    "description_match": 1.0  # Description was accurate
}
```

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
# or
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

# API docs available at http://localhost:8000/docs
```

## Usage

### Python API

```python
from server.code_review_env import CodeReviewEnvironment
from models import CodeReviewAction

# Initialize
env = CodeReviewEnvironment(task_id="bug_logic")

# Run episode
obs = env.reset()
print(f"Review this code:\n{obs.pr_info['code']}")

# Agent submits review
action = CodeReviewAction(
    review_text="The code has a bug...",
    findings=[
        {
            "type": "logic",
            "severity": "critical",
            "location": "line 3",
            "description": "Doesn't handle negative numbers",
            "suggestion": "Initialize with float('-inf')"
        }
    ]
)

result = env.step(action)
print(f"Reward: {result.reward}")
print(f"Total Score: {result.cumulative_score}")

env.close()
```

### HTTP API

After starting the server:

```bash
# Reset environment
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "readability", "task_index": 0}'

# Take a step
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"review_text": "...", "findings": []}}'
```

## Development

### Project Structure

```
code_review_env/
├── __init__.py              # Package exports
├── models.py                 # Typed models (Action, Observation, State)
├── rubric.py                 # Grading system
├── server/
│   ├── __init__.py
│   ├── app.py               # FastAPI server
│   ├── code_review_env.py   # Environment class
│   ├── Dockerfile           # Container image
│   └── tasks/
│       └── task_data.py     # Sample PRs for grading
├── baseline_inference.py    # Baseline benchmark script
├── openenv.yaml             # Environment manifest
└── README.md                # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Validating Environment

```bash
# Install OpenEnv CLI
pip install openenv

# Validate the environment
openenv validate --verbose
```

## Deployment

### Deploy to Hugging Face Spaces

```bash
# Login to Hugging Face
huggingface-cli login

# Push to Hub
openenv push --repo-id your-username/code-review-env
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for baseline | Required |
| `HF_TOKEN` | Hugging Face token | Required for push |

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [OpenEnv](https://github.com/meta-pytorch/OpenEnv)
- Inspired by professional code review workflows
- Designed for RL agent training
