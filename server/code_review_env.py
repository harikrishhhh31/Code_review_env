
import uuid
import random
import re
import copy
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
    
                                               
                                
    MAX_STEPS_PER_EPISODE = 10
    MAX_FINDINGS_PER_STEP = 7
    _GLOBAL_TASK: Optional[Dict[str, Any]] = None
    _GLOBAL_STATE: Optional[Dict[str, Any]] = None
    
                                                           
                                                                               
    SUPPORTS_CONCURRENT_SESSIONS = False
    
    def __init__(
        self,
        task_id: Optional[str] = None,
        task_index: int = 0,
        seed: Optional[int] = None
    ):
                                               
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
        return self._state
    
    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task_index: Optional[int] = 0,
        **kwargs
    ) -> CodeReviewObservation:
                                                 
        new_episode_id = episode_id or str(uuid.uuid4())
        
                                      
        if task_id is not None:
            self._state.task_id = task_id
                                             
            self._rubric = RubricFactory.create(task_id)
        
                                            
        if task_index is None:
            self._current_task = get_random_task(
                difficulty=self._state.task_id,
                seed=seed
            )
        else:
            self._current_task = get_task_by_id(
                self._state.task_id,
                task_index
            )
        
                     
        self._state.episode_id = new_episode_id
        self._state.step_count = 0
        self._state.task_index = task_index or 0
        self._state.total_reward = 0.01
        self._state.agent_findings_history = []
        issues = list(self._current_task["ground_truth_issues"])
        rng = random.Random(seed or uuid.uuid4().int)
        rng.shuffle(issues)
        self._current_task["ground_truth_issues"] = issues
        self._state.ground_truth_issues = issues
        self._state.current_pr = self._current_task["pr_info"]

        CodeReviewEnvironment._GLOBAL_TASK = copy.deepcopy(self._current_task)
        CodeReviewEnvironment._GLOBAL_STATE = {
            "task_id": self._state.task_id,
            "task_index": self._state.task_index,
            "step_count": self._state.step_count,
            "total_reward": self._state.total_reward,
        }
        
                            
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
                "readability": 0.01,
                "logic": 0.01,
                "security": 0.01,
                "description_match": 0.01,
                "readability_score": 0.01,
                "logic_score": 0.01,
                "security_score": 0.01,
                "description_match_score": 0.01,
                "bug_logic": 0.01,
                "full_review": 0.01,
            },
            findings_graded=[],
            reward=0.01,                       
            cumulative_score=0.01,
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
                                
        self._state.step_count += 1

                                                      
        if self._current_task is None:
            if CodeReviewEnvironment._GLOBAL_TASK is None:
                raise RuntimeError(
                    "Environment not initialized. Call reset() before step()."
                )
            self._current_task = copy.deepcopy(CodeReviewEnvironment._GLOBAL_TASK)
            snapshot = CodeReviewEnvironment._GLOBAL_STATE or {}
            self._state.task_id = snapshot.get("task_id", self._state.task_id)
            self._state.task_index = snapshot.get("task_index", 0)
            self._state.step_count = snapshot.get("step_count", 0)
            self._state.total_reward = snapshot.get("total_reward", 0.01)
            self._state.ground_truth_issues = self._current_task["ground_truth_issues"]
            self._state.current_pr = self._current_task["pr_info"]

        sanitized_action, penalty_overflow = self._sanitize_action(action)
        self._state.agent_findings_history.extend(sanitized_action.findings)
        
                                        
                                                      
        grading_observation = CodeReviewObservation(
            pr_info=self._current_task["pr_info"],
            metadata={
                "ground_truth_issues": self._current_task["ground_truth_issues"]
            }
        )
        
                                       
                                          
        reward = self._rubric(sanitized_action, grading_observation)

        score_breakdown = self._compute_score_breakdown(sanitized_action)

        is_done = self._check_episode_done()

        findings_graded = self._grade_findings(sanitized_action)
        penalty_false_positives = self._false_positive_penalty(findings_graded)
        reward = reward + penalty_overflow + penalty_false_positives
        reward = max(min(reward, 0.99), 0.01)

        self._step_rewards.append(reward)
        self._state.total_reward += reward
        if self._state.total_reward > 0.99:
            self._state.total_reward = 0.99

        CodeReviewEnvironment._GLOBAL_TASK = copy.deepcopy(self._current_task)
        CodeReviewEnvironment._GLOBAL_STATE = {
            "task_id": self._state.task_id,
            "task_index": self._state.task_index,
            "step_count": self._state.step_count,
            "total_reward": self._state.total_reward,
        }

        feedback = self._generate_feedback(sanitized_action, reward, score_breakdown)

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
                "penalty_overflow": penalty_overflow,
                "penalty_false_positives": penalty_false_positives,
                "task_id": self._state.task_id,
            }
        )
        
        return observation
    
    def close(self) -> None:
                                                             
                                              
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "CodeReviewEnv",
            "version": "1.0.0",
            "description": "AI-powered Pull Request code review environment",
            "tasks": ["readability", "bug_logic", "full_review"],
            "max_steps": self.MAX_STEPS_PER_EPISODE,
        }
    
                                                                               
                    
                                                                               
    
    def _get_task_description(self) -> str:
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
                         
        if self._state.step_count >= self._state.max_steps:
            return True
        
        return False
    
    def _compute_score_breakdown(
        self,
        action: CodeReviewAction
    ) -> Dict[str, float]:
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
        
                                           
        breakdown: Dict[str, float] = {
            "readability": 0.01,
            "logic": 0.01,
            "security": 0.01,
            "description_match": 0.01,
            "readability_score": 0.01,
            "logic_score": 0.01,
            "security_score": 0.01,
            "description_match_score": 0.01,
            "bug_logic": 0.01,
            "full_review": 0.01,
        }
        breakdown[self._state.task_id] = 0.01
        for itype in set(list(found_by_type.keys()) + list(gt_by_type.keys())):
            found = found_by_type.get(itype, 0)
            expected = gt_by_type.get(itype, 0)
            
            if found == 0:
                raw = 0.01
            elif expected == 0:
                raw = 0.5                                           
            else:
                                                                  
                raw = min(found / expected, 0.99)
                if raw < 0.01:
                    raw = 0.01
            breakdown[itype] = raw
            breakdown[f"{itype}_score"] = raw
        
        return breakdown
    
    def _grade_findings(self, action: CodeReviewAction) -> List[Dict[str, Any]]:
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
        if finding.get("type") != gt_issue.get("type"):
            return False
        
        finding_desc = finding.get("description", "").lower()
        gt_desc = gt_issue.get("description", "").lower()
        
        gt_words = [w for w in gt_desc.split() if len(w) > 4]
        matches = sum(1 for w in gt_words if w in finding_desc)
        if matches < 1:
            return False
        
        agent_loc = str(finding.get("location", "")).lower()
        gt_loc = str(gt_issue.get("location", "")).lower()
        return self._location_match(agent_loc, gt_loc)

    def _location_match(self, agent_loc: str, gt_loc: str) -> bool:
        if not agent_loc or not gt_loc:
            return True
        agent_tokens = [t for t in re.split(r"[^a-z0-9]+", agent_loc) if t]
        gt_tokens = [t for t in re.split(r"[^a-z0-9]+", gt_loc) if t]
        if not agent_tokens or not gt_tokens:
            return True
        overlap = set(agent_tokens) & set(gt_tokens)
        return len(overlap) > 0
    
    def _generate_feedback(
        self,
        action: CodeReviewAction,
        reward: float,
        score_breakdown: Dict[str, float]
    ) -> str:
                                
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

    def _sanitize_action(
        self,
        action: CodeReviewAction
    ) -> tuple[CodeReviewAction, float]:
        findings = action.findings
        if len(findings) <= self.MAX_FINDINGS_PER_STEP:
            return action, 0.0
        trimmed = findings[: self.MAX_FINDINGS_PER_STEP]
        overflow = len(findings) - self.MAX_FINDINGS_PER_STEP
        penalty = min(0.05 * overflow, 0.3) * -1.0
        new_action = action.model_copy(update={"findings": trimmed})
        return new_action, penalty

    def _false_positive_penalty(
        self,
        findings_graded: List[Dict[str, Any]]
    ) -> float:
        false_positives = sum(1 for f in findings_graded if not f.get("correct"))
        if false_positives == 0:
            return 0.0
        penalty = min(0.05 * false_positives, 0.3) * -1.0
        return penalty


                                                                               
         
                                                                               

__all__ = ["CodeReviewEnvironment"]
