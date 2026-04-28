from openenv.core.env_server import create_app
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi import FastAPI

from .code_review_env import CodeReviewEnvironment
from models import CodeReviewAction, CodeReviewObservation, CodeReviewState

app = create_app(
    env=CodeReviewEnvironment,
    action_cls=CodeReviewAction,
    observation_cls=CodeReviewObservation,
    env_name="code_review_env",
)


@app.get("/")
async def root():
    """HF Space App tab loads `/` by default; OpenEnv API lives under documented routes."""
    return JSONResponse(
        {
            "service": "code_review_env",
            "openenv": True,
            "health": "/health",
            "reset": "POST /reset",
            "docs": "/docs",
        }
    )


@app.get("/tasks")
async def list_tasks():
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
    from server.tasks.task_data import get_task_by_id
    
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
    counts = {}
    for issue in issues:
        itype = issue.get("type", "other")
        counts[itype] = counts.get(itype, 0) + 1
    return counts


@app.get("/demo", response_class=HTMLResponse)
async def demo_visual():
    """Live demo showing the full RL training loop with visual output"""
    
    # Run the demo
    env = CodeReviewEnvironment(task_id="readability")
    obs = env.reset()
    
    action = CodeReviewAction(
        review_text="Found multiple readability issues with variable naming and lack of documentation",
        findings=[
            {
                "type": "readability",
                "severity": "medium",
                "location": "function calc",
                "description": "Function name 'calc' is too vague",
                "suggestion": "Rename to 'calculate_sum' for clarity"
            },
            {
                "type": "readability",
                "severity": "high",
                "location": "line 1-3",
                "description": "No docstrings or comments provided",
                "suggestion": "Add docstring documenting function purpose"
            },
            {
                "type": "readability",
                "severity": "medium",
                "location": "line 2",
                "description": "Variable names 'z', 'a', 'b' are non-descriptive",
                "suggestion": "Use meaningful names like 'sum_result', 'first_num', 'second_num'"
            }
        ],
        confidence=0.85,
        review_category="readability"
    )
    
    result = env.step(action)
    
    # Create HTML response
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CodeReviewEnv - Live Demo</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f6f8fa;
                color: #333;
            }}
            .container {{
                background: white;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #24292e;
                border-bottom: 3px solid #0366d6;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #0366d6;
                margin-top: 30px;
                border-left: 4px solid #0366d6;
                padding-left: 10px;
            }}
            .step {{
                background: #f6f8fa;
                padding: 20px;
                margin: 15px 0;
                border-radius: 6px;
                border-left: 4px solid #0366d6;
            }}
            .code {{
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 6px;
                font-family: 'Monaco', 'Courier New', monospace;
                overflow-x: auto;
                margin: 10px 0;
            }}
            .metric {{
                display: inline-block;
                background: white;
                border: 1px solid #e1e4e8;
                padding: 10px 20px;
                margin: 5px;
                border-radius: 6px;
                font-weight: 600;
            }}
            .metric.positive {{
                color: #28a745;
                border-color: #28a745;
                background: #f0f9f4;
            }}
            .metric.neutral {{
                color: #6f42c1;
                border-color: #6f42c1;
                background: #f5f0ff;
            }}
            .finding {{
                background: white;
                border: 1px solid #e1e4e8;
                padding: 15px;
                margin: 10px 0;
                border-radius: 6px;
                border-left: 4px solid #0366d6;
            }}
            .finding.correct {{
                border-left-color: #28a745;
            }}
            .finding.incorrect {{
                border-left-color: #d73a49;
            }}
            .finding-header {{
                font-weight: 600;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            .badge.correct {{
                background: #28a745;
                color: white;
            }}
            .badge.incorrect {{
                background: #d73a49;
                color: white;
            }}
            .badge.severity-high {{
                background: #d73a49;
                color: white;
            }}
            .badge.severity-medium {{
                background: #ffc107;
                color: #333;
            }}
            .reward-box {{
                background: linear-gradient(135deg, #0366d6 0%, #6f42c1 100%);
                color: white;
                padding: 30px;
                border-radius: 8px;
                text-align: center;
                margin: 20px 0;
            }}
            .reward-box h3 {{
                margin: 0;
                font-size: 0.9em;
                opacity: 0.9;
            }}
            .reward-box .value {{
                font-size: 3em;
                font-weight: bold;
                margin: 10px 0;
            }}
            .score-breakdown {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .score-item {{
                background: white;
                border: 1px solid #e1e4e8;
                padding: 15px;
                border-radius: 6px;
                text-align: center;
            }}
            .score-item .label {{
                font-size: 0.9em;
                color: #666;
                margin-bottom: 8px;
            }}
            .score-item .value {{
                font-size: 1.8em;
                font-weight: bold;
                color: #0366d6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 CodeReviewEnv - Live Demo</h1>
            
            <h2>Step 1: Agent Receives PR to Review</h2>
            <div class="step">
                <strong>PR Title:</strong> {obs.pr_info['title']}<br>
                <strong>Language:</strong> {obs.pr_info['language']}<br>
                <strong>Files Changed:</strong> {', '.join(obs.pr_info['files_changed'])}
                
                <div class="code">{obs.pr_info['code']}</div>
            </div>
            
            <h2>Step 2: Agent Submits Review</h2>
            <div class="step">
                <strong>Review:</strong> {action.review_text}<br><br>
                <strong>Confidence:</strong> {action.confidence}<br>
                <strong>Findings Submitted:</strong> {len(action.findings)}
                
                <div style="margin-top: 15px;">
                    {''.join([f'''
                    <div class="finding">
                        <div class="finding-header">
                            <span>{finding['type'].upper()} - {finding['location']}</span>
                            <span class="badge severity-{finding['severity']}">{finding['severity']}</span>
                        </div>
                        <p><strong>Issue:</strong> {finding['description']}</p>
                        <p><strong>Suggestion:</strong> {finding['suggestion']}</p>
                    </div>
                    ''' for finding in action.findings])}
                </div>
            </div>
            
            <h2>Step 3: Environment Grades the Review</h2>
            
            <div class="reward-box">
                <h3>Reward Signal (Step Reward)</h3>
                <div class="value">+{result.reward:.3f}</div>
                <p style="margin: 0;">Positive feedback: Agent found real issues!</p>
            </div>
            
            <div class="metric positive">📊 Cumulative Score: {result.cumulative_score:.3f}</div>
            <div class="metric positive">✅ Episode Status: {'In Progress' if not result.done else 'Complete'}</div>
            <div class="metric neutral">🎯 Step: {env.state.step_count}/10</div>
            
            <h3 style="color: #0366d6;">Score Breakdown by Category:</h3>
            <div class="score-breakdown">
                <div class="score-item">
                    <div class="label">Readability</div>
                    <div class="value">{result.score_breakdown.get('readability_score', 0):.2f}</div>
                </div>
                <div class="score-item">
                    <div class="label">Logic/Bugs</div>
                    <div class="value">{result.score_breakdown.get('logic_score', 0):.2f}</div>
                </div>
                <div class="score-item">
                    <div class="label">Security</div>
                    <div class="value">{result.score_breakdown.get('security_score', 0):.2f}</div>
                </div>
                <div class="score-item">
                    <div class="label">Description Match</div>
                    <div class="value">{result.score_breakdown.get('description_match_score', 0):.2f}</div>
                </div>
            </div>
            
            <h3 style="color: #0366d6;">Findings Evaluation:</h3>
            {''.join([f'''
            <div class="finding {'correct' if graded['correct'] else 'incorrect'}">
                <div class="finding-header">
                    <span>{graded['finding']['type'].upper()} - {graded['finding']['location']}</span>
                    <span class="badge {'correct' if graded['correct'] else 'incorrect'}">
                        {'✓ CORRECT' if graded['correct'] else '✗ INCORRECT'}
                    </span>
                </div>
                <p><strong>Issue:</strong> {graded['finding']['description']}</p>
                <p><strong>Points Earned:</strong> {graded['points']}</p>
            </div>
            ''' for graded in result.findings_graded])}
            
            <h2>How This Works</h2>
            <div class="step">
                <p><strong>Dense Rewards:</strong> Agent gets feedback at every step, enabling faster learning</p>
                <p><strong>Ground Truth Matching:</strong> Each finding is graded against the actual issues in the code</p>
                <p><strong>Precision Matters:</strong> False positives reduce the reward (agent learns not to hallucinate)</p>
                <p><strong>Scalable:</strong> This gym works with hundreds of PR samples for training robust code review agents</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content


                                                                               
                                      
                                                                               

def main() -> None:
    import os

    import uvicorn

    port = int(os.environ.get("PORT", "7860"))
    print(f"Starting CodeReviewEnv server on port {port}...")
    print(f"API docs available at: http://0.0.0.0:{port}/docs")

    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
