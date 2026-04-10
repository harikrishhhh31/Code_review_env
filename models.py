
from typing import Optional, List, Dict, Any, Literal
from pydantic import Field

                                                        
                                                                   
from openenv.core.env_server.types import Action, Observation, State


                                                                               
                                              
                                                                               
                                                                    
                                                          

class CodeReviewAction(Action):
    
                                                                 
    review_text: str = Field(
        default="",
        description="The agent's code review as natural language text"
    )
    
                                                                    
                                                                     
    findings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="""Structured list of issues found.
        Each finding should contain:
        - type: 'readability' | 'logic' | 'security' | 'other'
        - severity: 'low' | 'medium' | 'high' | 'critical'
        - location: Where in code (e.g., 'line 5', 'function authenticate')
        - description: What's wrong
        - suggestion: How to fix (optional)
        """
    )
    
                                                                    
    confidence: float = Field(
        default=0.5,
        ge=0.0,                  
        le=1.0,                  
        description="Agent's confidence in this review (0.0 to 1.0)"
    )
    
                                                                            
    review_category: Literal["readability", "bug_logic", "full_review"] = Field(
        default="full_review",
        description="Which type of review this is"
    )


                                                                               
                                                 
                                                                               
                                                                    
                                                       

class CodeReviewObservation(Observation):
    
                                                       
    pr_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="""Pull Request information containing:
        - title: PR title
        - description: PR description
        - code: Code to review
        - language: Programming language
        - files_changed: List of files (for full review)
        """
    )
    
                                                                  
    feedback: str = Field(
        default="",
        description="Feedback from the environment on the agent's review"
    )
    
                                                                           
    score_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="""Breakdown of scores by category:
        - readability_score: How well agent identified readability issues
        - logic_score: How well agent identified bugs
        - security_score: How well agent identified security issues
        - description_match_score: Did agent correctly verify PR description
        """
    )
    
                                                               
    findings_graded: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="""Agent's findings with correctness evaluation:
        Each entry: {finding, correct: bool, points: float}
        """
    )
    
                                                           
                                                   
    reward: float = Field(
        default=0.0,
        description="""Reward signal for this step (can be positive or negative).
        
        RL LEARNING: How rewards work:
        - Positive reward: Agent did something good (found a real bug)
        - Negative reward: Agent did something bad (false positive)
        - Zero: Neutral action
        
        We use DENSE rewards (rewards at each step) not SPARSE rewards
        (only at end). Dense rewards help the agent learn faster!
        """
    )
    
                                                  
    cumulative_score: float = Field(
        default=0.0,
        description="Running total of all rewards in this episode"
    )
    
                       
    done: bool = Field(
        default=False,
        description="Whether this episode is complete (task finished or max steps)"
    )
    
                                                        
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (step count, task ID, etc.)"
    )


                                                                               
                                                  
                                                                               
                                                               
                                                                 
                                                             

class CodeReviewState(State):
    
                                        
    episode_id: str = Field(
        default="",
        description="Unique ID for this episode (for tracking/logging)"
    )
    
                                          
    step_count: int = Field(
        default=0,
        description="Number of actions taken in this episode"
    )
    
                                                        
    max_steps: int = Field(
        default=10,
        description="Maximum steps before episode ends"
    )
    
                                  
    task_id: Literal["readability", "bug_logic", "full_review"] = Field(
        default="full_review",
        description="Which task is currently active"
    )
    
                                                    
    task_index: int = Field(
        default=0,
        description="Index of current task in the task list"
    )
    
                                                      
                                                     
    ground_truth_issues: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Issues that exist in the code (for grading, hidden from agent)"
    )
    
                                       
    agent_findings_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="All findings the agent has submitted this episode"
    )
    
                          
    total_reward: float = Field(
        default=0.0,
        description="Cumulative reward for this episode"
    )
    
                                       
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducibility"
    )
    
                                             
    current_pr: Dict[str, Any] = Field(
        default_factory=dict,
        description="Current Pull Request data being reviewed"
    )


                                                                               
                                                     
                                                                               

class Finding:
    
                       
    ISSUE_TYPES = ["readability", "logic", "security", "other"]
    
                           
    SEVERITY_LEVELS = ["low", "medium", "high", "critical"]
    
    @staticmethod
    def create(
        issue_type: str,
        location: str,
        description: str,
        severity: str = "medium",
        suggestion: str = ""
    ) -> Dict[str, Any]:
                         
        if issue_type not in Finding.ISSUE_TYPES:
            raise ValueError(f"Invalid issue_type: {issue_type}")
        if severity not in Finding.SEVERITY_LEVELS:
            raise ValueError(f"Invalid severity: {severity}")
        
        return {
            "type": issue_type,
            "severity": severity,
            "location": location,
            "description": description,
            "suggestion": suggestion
        }


                                                                               
                                                                      
                                                                               

__all__ = [
    "CodeReviewAction",                           
    "CodeReviewObservation",                        
    "CodeReviewState",                                  
    "Finding",                                            
]
