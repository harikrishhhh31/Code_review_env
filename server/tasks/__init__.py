"""
tasks package - Task definitions and sample data
"""

from .task_data import (
    TASK1_PR_POOL,
    TASK2_PR_POOL,
    TASK3_PR_POOL,
    EASY_TASKS,
    MEDIUM_TASKS,
    HARD_TASKS,
    ALL_TASKS,
    get_task_by_id,
    get_random_task,
)

__all__ = [
    "TASK1_PR_POOL",
    "TASK2_PR_POOL",
    "TASK3_PR_POOL",
    "EASY_TASKS",
    "MEDIUM_TASKS",
    "HARD_TASKS",
    "ALL_TASKS",
    "get_task_by_id",
    "get_random_task",
]
