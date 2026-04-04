"""
client.py - EnvClient for CodeReviewEnv
========================================

This file provides a client class that connects to the CodeReviewEnv server.
Agents use this client to interact with the environment over HTTP/WebSocket.

LEARNING: Why a Client?
In production RL systems:
1. The environment might run on a different machine
2. The agent might run in a different container
3. Need persistent connections for lower latency

The client handles:
- Connection management (connect/disconnect)
- Serialization (Python objects → JSON)
- Deserialization (JSON → Python objects)
- Error handling

USAGE:
    from code_review_env import CodeReviewEnv, CodeReviewAction
    
    # Create client (connects to server)
    client = CodeReviewEnv(base_url="http://localhost:8000")
    
    # Use context manager (recommended)
    with client:
        obs = client.reset(task_id="readability")
        result = client.step(CodeReviewAction(...))
        state = client.state()
    
    # Or manually manage connection
    try:
        client = CodeReviewEnv(base_url="http://localhost:8000")
        result = client.reset()
        # ... use environment
    finally:
        client.close()
"""

from typing import Optional, Dict, Any
from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult

                         
from models import CodeReviewAction, CodeReviewObservation, CodeReviewState


class CodeReviewEnv(EnvClient[CodeReviewAction, CodeReviewObservation, CodeReviewState]):
    """
    Client for CodeReviewEnv server.
    
    This client connects to a CodeReviewEnv server (either local or remote)
    and provides a Pythonic interface for interacting with the environment.
    
    Example:
        # Connect to local server
        client = CodeReviewEnv(base_url="http://localhost:8000")
        
        # Reset environment
        result = client.reset(task_id="readability")
        print(f"PR: {result.observation.pr_info['title']}")
        
        # Submit review
        result = client.step(CodeReviewAction(
            review_text="Found issues...",
            findings=[...]
        ))
        print(f"Score: {result.observation.cumulative_score}")
        
        # Get state
        state = client.state()
        print(f"Steps: {state.step_count}")
        
        client.close()
    
    Or with context manager:
        with CodeReviewEnv(base_url="http://localhost:8000") as client:
            result = client.reset(task_id="bug_logic")
            result = client.step(CodeReviewAction(...))
    """
    
    def _step_payload(self, action: CodeReviewAction) -> Dict[str, Any]:
        """
        Convert action to dictionary for API request.
        
        This is called by the base class when sending actions to the server.
        Override this if you need custom serialization.
        
        Args:
            action: The action to serialize
        
        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            "review_text": action.review_text,
            "findings": action.findings,
            "confidence": action.confidence,
            "review_category": action.review_category,
        }
    
    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[CodeReviewObservation]:
        """
        Parse API response into StepResult.
        
        This is called by the base class after receiving a response.
        Override this to customize how responses are parsed.
        
        Args:
            payload: Response dictionary from server
        
        Returns:
            StepResult with parsed observation
        """
                                  
        obs_data = payload.get("observation", {})
        
                                   
        observation = CodeReviewObservation(
            pr_info=obs_data.get("pr_info", {}),
            feedback=obs_data.get("feedback", ""),
            score_breakdown=obs_data.get("score_breakdown", {}),
            findings_graded=obs_data.get("findings_graded", []),
            reward=obs_data.get("reward", 0.0),
            cumulative_score=obs_data.get("cumulative_score", 0.0),
            done=obs_data.get("done", False),
            metadata=obs_data.get("metadata", {}),
        )
        
                          
        reward = obs_data.get("reward", 0.0)
        done = obs_data.get("done", False)
        
        return StepResult(
            observation=observation,
            reward=reward,
            done=done,
        )
    
    def _parse_state(self, payload: Dict[str, Any]) -> CodeReviewState:
        """
        Parse state from API response.
        
        Called when retrieving current state via state() method.
        
        Args:
            payload: Response dictionary from server
        
        Returns:
            CodeReviewState object
        """
        return CodeReviewState(
            episode_id=payload.get("episode_id", ""),
            step_count=payload.get("step_count", 0),
            task_id=payload.get("task_id", "readability"),
            task_index=payload.get("task_index", 0),
            total_reward=payload.get("total_reward", 0.0),
        )
    
                                                                               
                         
                                                                               
                                                                 
    
    def reset_readability(self) -> StepResult[CodeReviewObservation]:
        """Reset for readability review task."""
        return self.reset(task_id="readability")
    
    def reset_bug_logic(self) -> StepResult[CodeReviewObservation]:
        """Reset for bug/logic review task."""
        return self.reset(task_id="bug_logic")
    
    def reset_full_review(self) -> StepResult[CodeReviewObservation]:
        """Reset for full PR review task."""
        return self.reset(task_id="full_review")


                                                                               
                 
                                                                               

class CodeReviewEnvFactory:
    """
    Factory for creating CodeReviewEnv clients.
    
    Provides convenient methods for connecting to different backends.
    """
    
    @staticmethod
    def from_docker_image(image_name: str) -> CodeReviewEnv:
        """
        Create client from a Docker image.
        
        Args:
            image_name: Name of the Docker image to use
        
        Returns:
            Configured CodeReviewEnv client
        """
                                                     
                                        
        return CodeReviewEnv(base_url="http://localhost:8000")
    
    @staticmethod
    def from_hub(repo_id: str) -> CodeReviewEnv:
        """
        Create client from Hugging Face Hub.
        
        Args:
            repo_id: HF Space identifier (e.g., "username/code-review-env")
        
        Returns:
            Configured CodeReviewEnv client
        """
        base_url = f"https://huggingface.co/spaces/{repo_id}"
        return CodeReviewEnv(base_url=base_url)


                                                                               
         
                                                                               

__all__ = [
    "CodeReviewEnv",
    "CodeReviewEnvFactory",
]
