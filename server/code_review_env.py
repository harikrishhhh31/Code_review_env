"""
code_review_env.py - Core Environment Class for CodeReviewEnv
=============================================================

This is the HEART of the RL environment. It implements the three essential methods:
1. reset() - Start a new episode
2. step() - Take an action and get feedback
3. state - Get current state (property)

LEARNING: What is an Environment in RL?
Think of an environment as a "game world" where the agent operates.
- The agent sees the environment's state (observation)
- The agent takes actions
- The environment responds with new observation + reward
- This loop continues until the episode ends

The OpenEnv Environment class is similar to OpenAI's Gymnasium Environment,
but with typed models and server/client architecture.

CORE CONCEPTS:
1. Episode: One complete task (from reset to done)
2. Step: One action taken by the agent
3. Observation: What the agent perceives
4. Reward: Feedback signal for learning
5. State: Internal tracking (hidden from agent)
"""

import uuid
from typing import Optional, Dict, Any, List
from openenv.core.env_server.interfaces import Environment

                         
from models import (
    CodeReviewAction,
    CodeReviewObservation,
    CodeReviewState,
)

                            
from rubric import RubricFactory, ReadabilityRubric, BugLogicRubric, FullReviewRubric

                                                                      
from .tasks.task_data import get_task_by_id, get_random_task


                                                                               
                        
                                                                               

class CodeReviewEnvironment(Environment):
    """
    Core RL Environment for Code Review tasks.
    
    This class manages:
    - Episode lifecycle (reset → step → done)
    - State tracking (hidden from agent)
    - Reward computation (via rubrics)
    - Task management (easy/medium/hard)
    
    LEARNING: The Environment is NOT the agent!
    - Environment: The "world" the agent operates in
    - Agent: The AI that makes decisions
    
    Think of it like:
    - Environment = The game/rules
    - Agent = The player
    
    USAGE:
        env = CodeReviewEnvironment()
        obs = env.reset()           # Start new episode
        obs = env.step(action)      # Take action
        state = env.state           # Get current state
        env.close()                 # Clean up
    """
    
                                               
                                
    MAX_STEPS_PER_EPISODE = 10
    
                                                           
                                                                               
    SUPPORTS_CONCURRENT_SESSIONS = True
    
    def __init__(
        self,
        task_id: Optional[str] = None,
        task_index: int = 0,
        seed: Optional[int] = None
    ):
        """
        Initialize the environment.
        
        Args:
            task_id: Which task to use ('readability', 'bug_logic', 'full_review')
                    If None, will be set during reset()
            task_index: Which PR in the task pool to use (for variety)
            seed: Random seed for reproducibility
        """
                                               
        super().__init__()
        
                          
        self._state = CodeReviewState(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            max_steps=self.MAX_STEPS_PER_EPISODE,
            task_id=task_id or "readability",
            task_index=task_index,
            seed=seed
        )
        
                                              
        self._rubric = RubricFactory.create(self._state.task_id)
        
                                                 
        self._current_task: Optional[Dict[str, Any]] = None
        
                                         
        self._step_rewards: List[float] = []
    
                                                                               
                                                         
                                                                               
    
    @property
    def state(self) -> CodeReviewState:
        """
        Get current environment state.
        
        IMPORTANT: State is INTERNAL - the agent shouldn't see this!
        This is used by:
        - The server to track episode progress
        - Grading systems to evaluate performance
        - Debugging when something goes wrong
        
        Returns:
            Current CodeReviewState
        """
        return self._state
    
    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task_index: int = 0,
        **kwargs
    ) -> CodeReviewObservation:
        """
        Reset the environment to start a new episode.
        
        RESET is called at the beginning of EVERY episode.
        Think of it as: "Starting a new game"
        
        What happens during reset:
        1. Generate new episode ID
        2. Load a new task (Pull Request to review)
        3. Initialize step counter
        4. Return initial observation to agent
        
        Args:
            seed: Random seed for reproducibility
            episode_id: Optional custom episode ID
            task_id: Which task type ('readability', 'bug_logic', 'full_review')
            task_index: Which PR in the pool (0 = first)
            **kwargs: Additional arguments (ignored)
        
        Returns:
            Initial observation (what the agent sees first)
        
        LEARNING: Why is reset important?
        - Ensures each episode starts fresh
        - Provides the first observation (agent sees PR to review)
        - Sets up ground truth for grading
        """
                                                 
        new_episode_id = episode_id or str(uuid.uuid4())
        
                                      
        if task_id is not None:
            self._state.task_id = task_id
                                             
            self._rubric = RubricFactory.create(task_id)
        
                                            
        self._current_task = get_task_by_id(
            self._state.task_id,
            task_index
        )
        
                     
        self._state.episode_id = new_episode_id
        self._state.step_count = 0
        self._state.task_index = task_index
        self._state.total_reward = 0.0
        self._state.agent_findings_history = []
        self._state.ground_truth_issues = (
            self._current_task["ground_truth_issues"]
        )
        self._state.current_pr = self._current_task["pr_info"]
        
                            
        self._step_rewards = []
        
                                    
                                            
        observation = CodeReviewObservation(
            pr_info=self._current_task["pr_info"],
            feedback=f"""You are reviewing a Pull Request.

Task: {self._get_task_description()}

PR Title: {self._current_task['pr_info']['title']}
PR Description: {self._current_task['pr_info']['description']}

Code to Review:
```{self._current_task['pr_info']['language']}
{self._current_task['pr_info']['code']}
```

Please review this code and provide your findings.""",
            score_breakdown={
                "readability": 0.0,
                "logic": 0.0,
                "security": 0.0,
                "description_match": 0.0
            },
            findings_graded=[],
            reward=0.0,                       
            cumulative_score=0.0,
            done=False,
            metadata={
                "task_id": self._state.task_id,
                "episode_id": new_episode_id,
            }
        )
        
        return observation
    
    def step(
        self,
        action: CodeReviewAction,
        timeout_s: Optional[float] = None,
        **kwargs
    ) -> CodeReviewObservation:
        """
        Take a step (action) in the environment.
        
        STEP is called for every action the agent takes.
        This is the core RL loop: observe → act → feedback
        
        What happens during step:
        1. Increment step counter
        2. Process agent's action (code review)
        3. Grade the action using rubric
        4. Compute reward
        5. Check if episode is done
        6. Return observation with feedback
        
        Args:
            action: The agent's action (CodeReviewAction with review findings)
            timeout_s: Optional timeout (ignored, for API compatibility)
            **kwargs: Additional arguments (ignored)
        
        Returns:
            Observation with feedback and reward
        
        LEARNING: The RL Step Loop
        ┌─────────────────────────────────────┐
        │ Observation → Agent Decision → Action │
        └─────────────────────────────────────┘
                     ↓
        ┌─────────────────────────────────────┐
        │  Environment: Grade + Reward → New   │
        │  Observation + Feedback              │
        └─────────────────────────────────────┘
                     ↓
        Loop back to agent
        
        REWARD DESIGN:
        We use DENSE rewards (reward at each step) not SPARSE rewards.
        Dense rewards help the agent learn faster because:
        - Immediate feedback: Agent knows if action was good
        - Credit assignment: Easier to link reward to action
        - Gradient signal: More frequent = better learning
        """
                                
        self._state.step_count += 1

                                                      
        if self._current_task is None:
            raise RuntimeError(
                "Environment not initialized. Call reset() before step()."
            )
        
                                
        self._state.agent_findings_history.extend(action.findings)
        
                                        
                                                      
        grading_observation = CodeReviewObservation(
            pr_info=self._current_task["pr_info"],
            metadata={
                "ground_truth_issues": self._current_task["ground_truth_issues"]
            }
        )
        
                                       
                                          
        reward = self._rubric(action, grading_observation)
        
                            
        self._step_rewards.append(reward)
        self._state.total_reward += reward
        
                                   
        score_breakdown = self._compute_score_breakdown(action)
        
                                      
        is_done = self._check_episode_done()
        
                                  
        feedback = self._generate_feedback(action, reward, score_breakdown)
        
                                   
        findings_graded = self._grade_findings(action)
        
                                  
        observation = CodeReviewObservation(
            pr_info=self._current_task["pr_info"],
            feedback=feedback,
            score_breakdown=score_breakdown,
            findings_graded=findings_graded,
            reward=reward,                                
            cumulative_score=self._state.total_reward,                
            done=is_done,
            metadata={
                "step": self._state.step_count,
                "max_steps": self._state.max_steps,
                "task_id": self._state.task_id,
            }
        )
        
        return observation
    
    def close(self) -> None:
        """
        Clean up resources when environment is destroyed.
        
        Called when:
        - Episode ends and environment is closed
        - Server shuts down
        - Cleanup is needed
        
        Override this if your environment uses:
        - Database connections
        - File handles
        - Network connections
        - GPU resources
        """
                                                             
                                              
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this environment.
        
        Used by:
        - Documentation generation
        - API responses
        - Environment registry
        
        Returns:
            Dictionary with environment metadata
        """
        return {
            "name": "CodeReviewEnv",
            "version": "1.0.0",
            "description": "AI-powered Pull Request code review environment",
            "tasks": ["readability", "bug_logic", "full_review"],
            "max_steps": self.MAX_STEPS_PER_EPISODE,
        }
    
                                                                               
                    
                                                                               
    
    def _get_task_description(self) -> str:
        """Get description of current task."""
        descriptions = {
            "readability": "Readability Review - Identify code style and clarity issues",
            "bug_logic": "Bug & Logic Review - Find logic errors and bugs",
            "full_review": "Full PR Review - Complete review including security and description accuracy",
        }
        return descriptions.get(
            self._state.task_id,
            "Code Review"
        )
    
    def _check_episode_done(self) -> bool:
        """
        Check if the current episode should end.
        
        Episode ends when:
        1. Agent has taken maximum steps (max_steps reached)
        2. OR agent explicitly indicates done
        
        Returns:
            True if episode should end
        """
                         
        if self._state.step_count >= self._state.max_steps:
            return True
        
        return False
    
    def _compute_score_breakdown(
        self,
        action: CodeReviewAction
    ) -> Dict[str, float]:
        """
        Calculate detailed score breakdown by category.
        
        This helps the agent understand:
        - How well did it find readability issues?
        - How well did it find logic bugs?
        - How well did it find security issues?
        
        Returns:
            Dictionary with scores for each category
        """
        if self._current_task is None:
            return {}

        findings = action.findings
        ground_truth = self._current_task["ground_truth_issues"]
        
                                
        found_by_type = {}
        gt_by_type = {}
        
        for finding in findings:
            ftype = finding.get("type", "other")
            found_by_type[ftype] = found_by_type.get(ftype, 0) + 1
        
        for issue in ground_truth:
            itype = issue.get("type", "other")
            gt_by_type[itype] = gt_by_type.get(itype, 0) + 1
        
                                           
        breakdown = {}
        for itype in set(list(found_by_type.keys()) + list(gt_by_type.keys())):
            found = found_by_type.get(itype, 0)
            expected = gt_by_type.get(itype, 0)
            
            if found == 0:
                breakdown[itype] = 0.0
            elif expected == 0:
                breakdown[itype] = 0.5                                           
            else:
                                                                  
                breakdown[itype] = min(found / expected, 1.0)
        
        return breakdown
    
    def _grade_findings(self, action: CodeReviewAction) -> List[Dict[str, Any]]:
        """
        Grade each individual finding the agent made.
        
        For each finding, we check:
        - Is it a true positive? (found a real issue)
        - Is it a false positive? (imagined issue)
        
        Returns:
            List of findings with correctness evaluation
        """
        if self._current_task is None:
            return []

        graded = []
        ground_truth = self._current_task["ground_truth_issues"]
        
        for finding in action.findings:
            is_correct = False
            points = 0.0
            
                                                            
            for gt_issue in ground_truth:
                if self._findings_match(finding, gt_issue):
                    is_correct = True
                                              
                    severity_points = {
                        "critical": 0.3,
                        "high": 0.2,
                        "medium": 0.15,
                        "low": 0.1
                    }
                    points = severity_points.get(
                        finding.get("severity", "medium"),
                        0.1
                    )
                    break
            
            graded.append({
                "finding": finding,
                "correct": is_correct,
                "points": points
            })
        
        return graded
    
    def _findings_match(
        self,
        finding: Dict[str, Any],
        gt_issue: Dict[str, Any]
    ) -> bool:
        """Check if agent finding matches ground truth issue."""
                       
        if finding.get("type") != gt_issue.get("type"):
            return False
        
                                       
        finding_desc = finding.get("description", "").lower()
        gt_desc = gt_issue.get("description", "").lower()
        
                                   
        gt_words = [w for w in gt_desc.split() if len(w) > 4]
        matches = sum(1 for w in gt_words if w in finding_desc)
        
        return matches >= 1                                 
    
    def _generate_feedback(
        self,
        action: CodeReviewAction,
        reward: float,
        score_breakdown: Dict[str, float]
    ) -> str:
        """
        Generate human-readable feedback for the agent.
        
        Good feedback helps the agent learn faster!
        
        Returns:
            Feedback string
        """
                                
        findings = action.findings
        by_type = {}
        for f in findings:
            t = f.get("type", "other")
            by_type[t] = by_type.get(t, 0) + 1
        
                        
        feedback_lines = [
            f"Step {self._state.step_count}/{self._state.max_steps}",
            f"Reward: {reward:.2f}",
            f"Total Score: {self._state.total_reward:.2f}",
            "",
            f"You found {len(findings)} issue(s):",
        ]
        
        for ftype, count in by_type.items():
            feedback_lines.append(f"  - {ftype}: {count}")
        
                                         
        if reward > 0.5:
            feedback_lines.append("\nGood work! Keep it up!")
        elif reward > 0.2:
            feedback_lines.append("\nMaking progress. Try to find more issues.")
        else:
            feedback_lines.append("\nReview the code more carefully.")
        
                       
        if self._check_episode_done():
            feedback_lines.append("")
            feedback_lines.append(f"Episode complete! Final score: {self._state.total_reward:.2f}")
        
        return "\n".join(feedback_lines)


                                                                               
         
                                                                               

__all__ = ["CodeReviewEnvironment"]
