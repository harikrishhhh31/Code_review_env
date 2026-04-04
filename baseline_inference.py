                      

import os
import json
import argparse
from typing import Dict, Any, Optional, List

                   
try:
    from openai import OpenAI
except ImportError:
    print("ERROR: OpenAI package not installed")
    print("Install with: pip install openai")
    exit(1)

                        
from models import CodeReviewAction, CodeReviewObservation
from server.code_review_env import CodeReviewEnvironment


                                                                               
               
                                                                               

                      
DEFAULT_MODEL = "gpt-4"

                                                         
DEFAULT_TEMPERATURE = 0.3

                            
DEFAULT_MAX_TOKENS = 1000


                                                                               
                
                                                                               

class BaselineAgent:
    
    SYSTEM_PROMPT = """You are an expert code reviewer. Your job is to:
1. Analyze code for issues
2. Identify bugs, security problems, and readability issues
3. Provide structured feedback

Be thorough but accurate. Only report issues you are confident about."""

    def __init__(self, model: str = DEFAULT_MODEL, api_key: Optional[str] = None):
        self.model = model
        
                                                   
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=key)
    
    def review_code(
        self,
        pr_title: str,
        pr_description: str,
        code: str,
        language: str,
        task_type: str
    ) -> Dict[str, Any]:
                                    
        if task_type == "readability":
            focus = "focus on readability and style issues"
        elif task_type == "bug_logic":
            focus = "focus on finding logic bugs and errors"
        else:
            focus = "comprehensively review for all issues (readability, bugs, security)"
        
        user_prompt = f"""Review this Pull Request:

Title: {pr_title}
Description: {pr_description}

Code to review (language: {language}):
```{language}
{code}
```

Please {focus}. Provide your review in two parts:

1. SUMMARY: A brief overview of your findings
2. FINDINGS: List of specific issues found (if any)

For each finding, include:
- Type (readability/logic/security)
- Severity (low/medium/high/critical)
- Location (where in the code)
- Description (what's wrong)
- Suggestion (how to fix)

Be specific and only report issues you are confident about."""

                         
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS
        )
        
        review_text = response.choices[0].message.content
        
                                      
        findings = self._parse_findings(review_text)
        
        return {
            "review_text": review_text,
            "findings": findings
        }
    
    def _parse_findings(self, review_text: str) -> List[Dict[str, Any]]:
        findings = []
        
                                         
                                                                             
        lines = review_text.split("\n")
        
        current_finding = None
        
        for line in lines:
            line = line.strip()
            
                                   
            if "type:" in line.lower():
                if current_finding:
                    findings.append(current_finding)
                current_finding = {
                    "type": self._extract_value(line, "type"),
                    "severity": "medium",
                    "location": "unspecified",
                    "description": "",
                    "suggestion": ""
                }
            
                                       
            elif "severity:" in line.lower():
                if current_finding:
                    current_finding["severity"] = self._extract_value(line, "severity")
            
                                       
            elif "location:" in line.lower():
                if current_finding:
                    current_finding["location"] = self._extract_value(line, "location")
            
                                  
            elif "description:" in line.lower() or "what's wrong:" in line.lower():
                if current_finding:
                    current_finding["description"] = self._extract_value(
                        line, "description"
                    )
            
                                 
            elif "suggestion:" in line.lower() or "fix:" in line.lower():
                if current_finding:
                    current_finding["suggestion"] = self._extract_value(
                        line, "suggestion"
                    )
        
                                       
        if current_finding:
            findings.append(current_finding)
        
                                                                            
        if not findings:
                                                   
            for line in lines:
                line_lower = line.lower()
                
                                                 
                if any(kw in line_lower for kw in ["bug", "error", "issue", "problem", "vulnerability", "security", "missing", "should"]):
                                              
                    if any(kw in line_lower for kw in ["security", "sql", "injection", "xss", "vulnerability"]):
                        ftype = "security"
                    elif any(kw in line_lower for kw in ["logic", "bug", "error", "wrong"]):
                        ftype = "logic"
                    else:
                        ftype = "readability"
                    
                    findings.append({
                        "type": ftype,
                        "severity": "medium",
                        "location": "see code",
                        "description": line.strip(" -:*"),
                        "suggestion": ""
                    })
        
        return findings[:10]                        
    
    def _extract_value(self, line: str, field: str) -> str:
        line_lower = line.lower()
        
                                        
        idx = line_lower.find(field + ":")
        if idx == -1:
            return ""
        
                                        
        value = line[idx + len(field) + 1:].strip()
        
                                  
        for prefix in ["**", "*", "-", " "]:
            if value.startswith(prefix):
                value = value[1:].strip()
        
        return value


                                                                               
                      
                                                                               

def run_task(
    agent: BaselineAgent,
    task_id: str,
    task_index: int = 0,
    verbose: bool = True
) -> Dict[str, Any]:
    if verbose:
        print(f"\n{'='*60}")
        print(f"Running task: {task_id} (index: {task_index})")
        print(f"{'='*60}")
    
                        
    env = CodeReviewEnvironment(task_id=task_id)
    
                       
    obs = env.reset(task_id=task_id, task_index=task_index)
    
    if verbose:
        print(f"\nPR Title: {obs.pr_info['title']}")
        print(f"PR Description: {obs.pr_info['description']}")
        print(f"\nCode to review:")
        print("-" * 40)
        print(obs.pr_info["code"])
        print("-" * 40)
    
                           
    review_result = agent.review_code(
        pr_title=obs.pr_info["title"],
        pr_description=obs.pr_info["description"],
        code=obs.pr_info["code"],
        language=obs.pr_info["language"],
        task_type=task_id
    )
    
    if verbose:
        print(f"\nAgent review:")
        print(review_result["review_text"])
        print(f"\nParsed {len(review_result['findings'])} findings")
    
                   
    action = CodeReviewAction(
        review_text=review_result["review_text"],
        findings=review_result["findings"],
        confidence=0.7,
        review_category=task_id
    )
    
                           
    result = env.step(action)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"RESULTS:")
        print(f"  Step reward: {result.reward:.3f}")
        print(f"  Cumulative score: {result.cumulative_score:.3f}")
        print(f"  Findings graded: {len(result.findings_graded)}")
        print(f"  Score breakdown: {result.score_breakdown}")
        print(f"  Episode done: {result.done}")
        print(f"{'='*60}")
    
    return {
        "task_id": task_id,
        "task_index": task_index,
        "reward": result.reward,
        "cumulative_score": result.cumulative_score,
        "findings_count": len(review_result["findings"]),
        "findings_graded": result.findings_graded,
        "score_breakdown": result.score_breakdown,
        "done": result.done,
        "feedback": result.feedback
    }


def run_all_tasks(
    agent: BaselineAgent,
    verbose: bool = True
) -> Dict[str, Any]:
    tasks = ["readability", "bug_logic", "full_review"]
    results = []
    
    for task_id in tasks:
                                 
        result = run_task(agent, task_id, task_index=0, verbose=verbose)
        results.append(result)
    
                             
    total_score = sum(r["cumulative_score"] for r in results)
    avg_score = total_score / len(results) if results else 0
    
    summary = {
        "total_tasks": len(results),
        "average_score": avg_score,
        "total_score": total_score,
        "results": results
    }
    
    return summary


                                                                               
               
                                                                               

def main():
    parser = argparse.ArgumentParser(
        description="Run baseline inference on CodeReviewEnv"
    )
    parser.add_argument(
        "--task",
        choices=["readability", "bug_logic", "full_review"],
        help="Specific task to run (default: all tasks)"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed output"
    )
    parser.add_argument(
        "--output",
        help="Output file for results (JSON)"
    )
    
    args = parser.parse_args()
    
                       
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OpenAI API key required")
        print("Set OPENAI_API_KEY environment variable or use --api-key")
        print("\nExample:")
        print("  export OPENAI_API_KEY=sk-...")
        print("  python baseline_inference.py")
        exit(1)
    
    print(f"Using model: {args.model}")
    
                  
    agent = BaselineAgent(model=args.model, api_key=api_key)
    
                    
    if args.task:
                         
        result = run_task(agent, args.task, verbose=args.verbose)
        summary = {
            "total_tasks": 1,
            "average_score": result["cumulative_score"],
            "results": [result]
        }
    else:
                       
        summary = run_all_tasks(agent, verbose=args.verbose)
    
                   
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tasks completed: {summary['total_tasks']}")
    print(f"Average score: {summary['average_score']:.3f}")
    print(f"Total score: {summary['total_score']:.3f}")
    
                            
    print("\nPer-task results:")
    for r in summary["results"]:
        print(f"  {r['task_id']}: {r['cumulative_score']:.3f}")
    
                               
    if args.output:
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    return summary


if __name__ == "__main__":
    main()
