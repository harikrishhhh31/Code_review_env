"""
CodeReviewEnv - AI-Powered Code Review Environment
===================================================

A reinforcement learning environment for training code review agents.
Agents learn to analyze pull requests, identify bugs, security issues,
and readability problems.

Quick Start:
    from server.code_review_env import CodeReviewEnvironment
    from models import CodeReviewAction

    env = CodeReviewEnvironment()
    obs = env.reset(task_id="readability")
    action = CodeReviewAction(review_text="...", findings=[])
    result = env.step(action)

For more examples, see README.md
"""

# Import main classes for easy access
from server.code_review_env import CodeReviewEnvironment
from models import (
    CodeReviewAction,
    CodeReviewObservation,
    CodeReviewState,
    Finding,
)

# Version
__version__ = "1.0.0"

# Public API
__all__ = [
    "CodeReviewEnvironment",
    "CodeReviewAction", 
    "CodeReviewObservation",
    "CodeReviewState",
    "Finding",
    "__version__",
]
