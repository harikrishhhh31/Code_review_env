
from typing import Optional, Dict, Any
from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult

                         
from models import CodeReviewAction, CodeReviewObservation, CodeReviewState


class CodeReviewEnv(EnvClient[CodeReviewAction, CodeReviewObservation, CodeReviewState]):
    
    def _step_payload(self, action: CodeReviewAction) -> Dict[str, Any]:
        return {
            "review_text": action.review_text,
            "findings": action.findings,
            "confidence": action.confidence,
            "review_category": action.review_category,
        }
    
    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[CodeReviewObservation]:
                                  
        obs_data = payload.get("observation", {})
        
                                   
        observation = CodeReviewObservation(
            pr_info=obs_data.get("pr_info", {}),
            feedback=obs_data.get("feedback", ""),
            score_breakdown=obs_data.get("score_breakdown", {}),
            findings_graded=obs_data.get("findings_graded", []),
            reward=obs_data.get("reward", 0.01),
            cumulative_score=obs_data.get("cumulative_score", 0.01),
            done=obs_data.get("done", False),
            metadata=obs_data.get("metadata", {}),
        )
        
                          
        reward = obs_data.get("reward", 0.01)
        done = obs_data.get("done", False)
        
        return StepResult(
            observation=observation,
            reward=reward,
            done=done,
        )
    
    def _parse_state(self, payload: Dict[str, Any]) -> CodeReviewState:
        return CodeReviewState(
            episode_id=payload.get("episode_id", ""),
            step_count=payload.get("step_count", 0),
            task_id=payload.get("task_id", "readability"),
            task_index=payload.get("task_index", 0),
            total_reward=payload.get("total_reward", 0.01),
        )
    
                                                                               
                         
                                                                               
                                                                 
    
    def reset_readability(self) -> StepResult[CodeReviewObservation]:
        return self.reset(task_id="readability")
    
    def reset_bug_logic(self) -> StepResult[CodeReviewObservation]:
        return self.reset(task_id="bug_logic")
    
    def reset_full_review(self) -> StepResult[CodeReviewObservation]:
        return self.reset(task_id="full_review")


                                                                               
                 
                                                                               

class CodeReviewEnvFactory:
    
    @staticmethod
    def from_docker_image(image_name: str) -> CodeReviewEnv:
                                                     
                                        
        return CodeReviewEnv(base_url="http://localhost:8000")
    
    @staticmethod
    def from_hub(repo_id: str) -> CodeReviewEnv:
        base_url = f"https://huggingface.co/spaces/{repo_id}"
        return CodeReviewEnv(base_url=base_url)


                                                                               
         
                                                                               

__all__ = [
    "CodeReviewEnv",
    "CodeReviewEnvFactory",
]
