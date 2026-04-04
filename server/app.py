"""
server/app.py - FastAPI Server for CodeReviewEnv
================================================

This file sets up the HTTP/WebSocket server that hosts the environment.
Agents connect to this server to interact with the environment.

LEARNING: Why a Server?
In production RL systems:
1. Environment might run on a different machine than the agent
2. Need to serve multiple agents simultaneously
3. Want to isolate environment (Docker) from agent

OpenEnv uses FastAPI for:
- HTTP endpoints for reset/step/state
- WebSocket for persistent connections (lower latency)
- Automatic API documentation

The server pattern:
┌─────────────┐      HTTP/WS      ┌─────────────┐
│   Agent     │ ←──────────────→ │   Server    │
│  (Client)   │                  │  (FastAPI)  │
└─────────────┘                  └──────┬──────┘
                                        │
                                        │ Creates
                                        ▼
                                 ┌─────────────┐
                                 │ Environment │
                                 │  Instance   │
                                 └─────────────┘
"""

from openenv.core.env_server import create_app

                                                                       
from .code_review_env import CodeReviewEnvironment
from models import CodeReviewAction, CodeReviewObservation, CodeReviewState

                                
                          
                                                    
                               
                                        
                                          

app = create_app(
                                               
                                                  
    env=CodeReviewEnvironment,
    
                                 
                                                   
    action_cls=CodeReviewAction,
    
                                      
                                             
    observation_cls=CodeReviewObservation,
    
                                                  
    env_name="code_review_env",
)


                                                                               
                            
                                                                               

                                              
                                  
                              
                                   
                            
                                  
                                                
                                            
                                         


                                                            
@app.get("/tasks")
async def list_tasks():
    """
    List all available review tasks.
    
    Returns:
        Dictionary with task categories and counts
    """
    return {
        "tasks": [
            {
                "id": "readability",
                "name": "Readability Review",
                "difficulty": "easy",
                "description": "Find code style and clarity issues"
            },
            {
                "id": "bug_logic",
                "name": "Bug & Logic Review", 
                "difficulty": "medium",
                "description": "Find logic errors and bugs"
            },
            {
                "id": "full_review",
                "name": "Full PR Review",
                "difficulty": "hard",
                "description": "Complete review with security and description check"
            }
        ],
        "total": 3
    }


                                              
@app.get("/tasks/{task_id}")
async def get_task_info(task_id: str):
    """
    Get details about a specific task.
    
    Args:
        task_id: One of 'readability', 'bug_logic', 'full_review'
    
    Returns:
        Task information including sample code
    """
    from tasks.task_data import get_task_by_id
    
    try:
        task = get_task_by_id(task_id, index=0)
        return {
            "task_id": task["task_id"],
            "title": task["pr_info"]["title"],
            "description": task["pr_info"]["description"],
            "language": task["pr_info"]["language"],
            "files_changed": task["pr_info"]["files_changed"],
            "issue_count": len(task["ground_truth_issues"]),
            "issues_by_type": _count_issues_by_type(task["ground_truth_issues"])
        }
    except KeyError:
        return {"error": f"Unknown task: {task_id}"}, 404


def _count_issues_by_type(issues):
    """Helper to count issues by type."""
    counts = {}
    for issue in issues:
        itype = issue.get("type", "other")
        counts[itype] = counts.get(itype, 0) + 1
    return counts


                                                                               
                                      
                                                                               

def main() -> None:
    """Entrypoint for running the server locally."""
    import uvicorn

                    
                                         
                                                  
    print("Starting CodeReviewEnv server...")
    print("API docs available at: http://localhost:8000/docs")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True                                           
    )


if __name__ == "__main__":
    main()
