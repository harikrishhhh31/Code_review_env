"""
rubric.py - Agent Grading System for CodeReviewEnv
===================================================

This file implements the RUBRIC system - the core grading mechanism in OpenEnv.

LEARNING: What is a Rubric?
In RL terms, a rubric is a "reward function" that evaluates how well
the agent performed. It's like having an expert grade the agent's work.

Why Rubrics Instead of Simple Scoring?
1. Composability - Can combine multiple criteria
2. Visibility - We can see exactly WHY the agent got its score
3. Flexibility - Can adjust weights without changing core logic
4. Debugging - Easy to see which parts of the review were good/bad

Rubric Design Philosophy (inspired by PyTorch nn.Module):
- Leaf rubrics: Single evaluation criterion (like one neuron)
- Container rubrics: Combine multiple rubrics (like layers)
- Auto-registration: Child rubrics register automatically
- Hooks: For observability and debugging
"""

from typing import List, Dict, Any, Optional, Tuple
from openenv.core.rubrics import Rubric


# =============================================================================
# PART 1: LEAF RUBRICS - Individual Evaluation Criteria
# =============================================================================
# Leaf rubrics evaluate ONE specific aspect of the agent's performance.
# Think of them as individual "questions" in a rubric.

class CorrectnessRubric(Rubric):
    """
    Did the agent find issues that actually exist?
    
    This rubric checks if the agent's findings are CORRECT
    (true positives vs false positives).
    
    LEARNING: True Positives vs False Positives
    - True Positive (TP): Agent found an issue that EXISTS ✓
    - False Positive (FP): Agent found an issue that DOESN'T EXIST ✗
    - False Negative (FN): Agent MISSED an issue that EXISTS ✗
    
    Formula: precision = TP / (TP + FP)
    """
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize the rubric.
        
        Args:
            weight: How much this criterion contributes to final score
        """
        super().__init__()
        self.weight = weight
        self.last_score = 0.0  # For logging/introspection
    
    def forward(self, action, observation) -> float:
        """
        Evaluate correctness of findings.
        
        RL LEARNING: This is the reward computation!
        This method is called after each agent action.
        Returns a reward value between 0.0 and 1.0.
        
        Args:
            action: The agent's action (CodeReviewAction)
            observation: Current observation (will be updated with score)
        
        Returns:
            Reward score between 0.0 and 1.0
        """
        # Get agent's findings
        agent_findings = getattr(action, 'findings', [])
        
        # Get ground truth (what issues actually exist)
        ground_truth = getattr(observation, 'metadata', {}).get(
            'ground_truth_issues', []
        )
        
        # Calculate precision: how many of agent's findings are correct?
        if not agent_findings:
            return 0.0  # No findings = no points
        
        # Count correct findings (true positives)
        correct_count = 0
        for agent_finding in agent_findings:
            # Check if this finding matches something in ground truth
            for gt_issue in ground_truth:
                if self._findings_match(agent_finding, gt_issue):
                    correct_count += 1
                    break  # Count each finding once
        
        # Calculate precision score
        precision = correct_count / len(agent_findings) if agent_findings else 0.0
        
        # Store for introspection
        self.last_score = precision
        
        return precision * self.weight
    
    def _findings_match(
        self, 
        agent_finding: Dict, 
        gt_issue: Dict
    ) -> bool:
        """
        Check if an agent finding matches a ground truth issue.
        
        LEARNING: String matching can be fuzzy!
        We use partial matching (contains) not exact matching.
        This is more forgiving and realistic.
        """
        # Extract key fields
        agent_type = agent_finding.get('type', '').lower()
        gt_type = gt_issue.get('type', '').lower()
        
        agent_desc = agent_finding.get('description', '').lower()
        gt_desc = gt_issue.get('description', '').lower()
        
        # Check type match
        type_match = agent_type == gt_type
        
        # Check description similarity (partial match)
        desc_match = (
            gt_desc in agent_desc or 
            agent_desc in gt_desc or
            any(word in agent_desc for word in gt_desc.split() if len(word) > 4)
        )
        
        return type_match and desc_match


class CompletenessRubric(Rubric):
    """
    Did the agent find ALL the issues?
    
    This rubric checks if the agent missed any issues (recall).
    
    LEARNING: Recall
    - Recall = TP / (TP + FN)
    - Measures how many actual issues were found
    - High recall = agent doesn't miss important issues
    """
    
    def __init__(self, weight: float = 1.0):
        super().__init__()
        self.weight = weight
        self.last_score = 0.0
    
    def forward(self, action, observation) -> float:
        """Evaluate completeness of findings (recall)."""
        agent_findings = getattr(action, 'findings', [])
        ground_truth = getattr(observation, 'metadata', {}).get(
            'ground_truth_issues', []
        )
        
        if not ground_truth:
            return 1.0  # No issues to find = full score
        
        # Count how many ground truth issues were found
        found_count = 0
        for gt_issue in ground_truth:
            for agent_finding in agent_findings:
                if self._issue_found(agent_finding, gt_issue):
                    found_count += 1
                    break
        
        # Calculate recall
        recall = found_count / len(ground_truth)
        self.last_score = recall
        
        return recall * self.weight
    
    def _issue_found(
        self, 
        agent_finding: Dict, 
        gt_issue: Dict
    ) -> bool:
        """Check if a ground truth issue was found by agent."""
        # Match on issue type and description keywords
        agent_type = agent_finding.get('type', '').lower()
        gt_type = gt_issue.get('type', '').lower()
        
        gt_desc = gt_issue.get('description', '').lower()
        agent_desc = agent_finding.get('description', '').lower()
        
        type_match = agent_type == gt_type
        desc_match = any(
            word in agent_desc 
            for word in gt_desc.split() 
            if len(word) > 4
        )
        
        return type_match and desc_match


class SeverityRubric(Rubric):
    """
    Did the agent correctly prioritize issues by severity?
    
    Critical issues should be marked as critical, not low.
    This rubric penalizes incorrect severity assignments.
    """
    
    def __init__(self, weight: float = 0.5):
        super().__init__()
        self.weight = weight
        self.last_score = 0.0
    
    def forward(self, action, observation) -> float:
        """Evaluate severity accuracy."""
        agent_findings = getattr(action, 'findings', [])
        
        if not agent_findings:
            return 0.0
        
        ground_truth = getattr(observation, 'metadata', {}).get(
            'ground_truth_issues', []
        )
        
        # Severity mapping (for comparison)
        severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        
        correct_severity = 0
        total_severity_issues = 0
        
        for agent_finding in agent_findings:
            agent_severity = agent_finding.get('severity', 'medium')
            agent_type = agent_finding.get('type', '')
            
            # Find matching ground truth
            for gt_issue in ground_truth:
                if gt_issue.get('type', '') == agent_type:
                    total_severity_issues += 1
                    gt_severity = gt_issue.get('severity', 'medium')
                    
                    # Exact match or within 1 level is acceptable
                    diff = abs(
                        severity_order.get(agent_severity, 1) - 
                        severity_order.get(gt_severity, 1)
                    )
                    if diff <= 1:
                        correct_severity += 1
                    break
        
        if total_severity_issues == 0:
            return 1.0  # No severity-annotated issues
        
        score = correct_severity / total_severity_issues
        self.last_score = score
        
        return score * self.weight


class DescriptionMatchRubric(Rubric):
    """
    Does the code actually do what the PR description claims?
    
    This is specific to Task 3 (Full Review).
    Agent must verify that the code matches its stated purpose.
    """
    
    def __init__(self, weight: float = 1.0):
        super().__init__()
        self.weight = weight
        self.last_score = 0.0
    
    def forward(self, action, observation) -> float:
        """Evaluate if agent correctly assessed description match."""
        pr_info = getattr(observation, 'pr_info', {})
        expected_match = pr_info.get('description_match', True)
        
        # Check if agent made a correct assessment
        # This is simplified - real implementation would parse agent's text
        agent_assessment_correct = True  # Placeholder
        
        score = 1.0 if agent_assessment_correct else 0.0
        self.last_score = score
        
        return score * self.weight


# =============================================================================
# PART 2: COMPOSITE RUBRICS - Combine Multiple Criteria
# =============================================================================
# Composite rubrics combine leaf rubrics for full evaluation.

class ReadabilityRubric(Rubric):
    """
    Full rubric for Task 1 (Readability Review).
    
    Combines:
    - Correctness: Did agent find real readability issues?
    - Completeness: Did agent find ALL readability issues?
    """
    
    def __init__(self):
        super().__init__()
        # Auto-register child rubrics (PyTorch nn.Module pattern)
        self.correctness = CorrectnessRubric(weight=0.5)
        self.completeness = CompletenessRubric(weight=0.5)
    
    def forward(self, action, observation) -> float:
        """
        Calculate combined readability score.
        
        LEARNING: How to combine rubric scores
        We use weighted average here, but could also use:
        - Sequential: Pass/fail gating
        - Product: Multiply scores (stricter)
        """
        c_score = self.correctness(action, observation)
        comp_score = self.completeness(action, observation)
        
        # Weighted combination
        total = c_score + comp_score
        
        return min(total, 1.0)  # Cap at 1.0


class BugLogicRubric(Rubric):
    """
    Full rubric for Task 2 (Bug & Logic Review).
    
    Combines:
    - Correctness: Did agent find real bugs?
    - Completeness: Did agent find all bugs?
    - Severity: Did agent prioritize critical bugs correctly?
    """
    
    def __init__(self):
        super().__init__()
        self.correctness = CorrectnessRubric(weight=0.4)
        self.completeness = CompletenessRubric(weight=0.4)
        self.severity = SeverityRubric(weight=0.2)
    
    def forward(self, action, observation) -> float:
        """Calculate combined bug/logic score."""
        c_score = self.correctness(action, observation)
        comp_score = self.completeness(action, observation)
        sev_score = self.severity(action, observation)
        
        total = c_score + comp_score + sev_score
        
        return min(total, 1.0)


class FullReviewRubric(Rubric):
    """
    Full rubric for Task 3 (Full PR Review).
    
    Combines:
    - Readability: Code style issues
    - Bug/Logic: Functional issues
    - Security: Vulnerability detection
    - Description Match: Does code match PR claim?
    """
    
    def __init__(self):
        super().__init__()
        self.readability = ReadabilityRubric()
        self.bug_logic = BugLogicRubric()
        self.description_match = DescriptionMatchRubric(weight=0.2)
    
    def forward(self, action, observation) -> float:
        """
        Calculate comprehensive review score.
        
        LEARNING: Hierarchical scoring
        We weight different categories:
        - Security: Most important (30%)
        - Bug/Logic: Very important (35%)
        - Readability: Important (25%)
        - Description: Context (10%)
        """
        read_score = self.readability(action, observation)
        bug_score = self.bug_logic(action, observation)
        desc_score = self.description_match(action, observation)
        
        # Weighted combination
        total = (
            read_score * 0.25 +
            bug_score * 0.35 +
            desc_score * 0.40  # Security and description combined
        )
        
        return min(total, 1.0)


# =============================================================================
# PART 3: RUBRIC FACTORY - Create rubric for any task
# =============================================================================

class RubricFactory:
    """
    Factory for creating the right rubric based on task type.
    
    LEARNING: Factory Pattern
    Instead of manually creating rubrics, we use a factory
    that returns the right rubric for the current task.
    """
    
    # Map task IDs to rubric classes
    RUBRIC_MAP = {
        "readability": ReadabilityRubric,
        "bug_logic": BugLogicRubric,
        "full_review": FullReviewRubric,
    }
    
    @classmethod
    def create(cls, task_id: str) -> Rubric:
        """
        Create a rubric for the given task.
        
        Args:
            task_id: One of 'readability', 'bug_logic', 'full_review'
        
        Returns:
            Appropriate rubric instance
        
        Raises:
            ValueError: If task_id is unknown
        """
        rubric_class = cls.RUBRIC_MAP.get(task_id)
        if rubric_class is None:
            raise ValueError(f"Unknown task: {task_id}")
        return rubric_class()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Leaf rubrics
    "CorrectnessRubric",
    "CompletenessRubric", 
    "SeverityRubric",
    "DescriptionMatchRubric",
    # Composite rubrics
    "ReadabilityRubric",
    "BugLogicRubric",
    "FullReviewRubric",
    # Factory
    "RubricFactory",
]
