import asyncio
import sys
from client import CodeReviewEnvFactory
from models import CodeReviewAction
import argparse

# Fix for windows encoding printing issues
sys.stdout.reconfigure(encoding='utf-8')

async def test_deployment(repo_id):
    # Connect to the Hugging Face space
    print(f"Connecting to environment on Hugging Face Space: {repo_id}...")
    env = CodeReviewEnvFactory.from_hub(repo_id)

    try:
        # 1. Start a new episode for the 'readability' task
        print("\n--- 1. Resetting Environment ('readability' task) ---")
        reset_result = await env.reset(task_id="readability")
        
        # The result contains the observation (PR info, etc.)
        obs = reset_result.observation
        pr_info = obs.pr_info
        
        print("Success! Environment is active.")
        print(f"PR to review: {pr_info.get('title', 'Unknown Title')}")
        print(f"Code language: {pr_info.get('language', 'Unknown')}")
        print("\nCode Snippet to Review:")
        print("-" * 40)
        print(pr_info.get('code', 'No code provided'))
        print("-" * 40)
        
        # 2. Perform a test 'step' (submit a dummy review action)
        print("\n--- 2. Submitting Test Action ---")
        action = CodeReviewAction(
            review_text="Test review: I found some missing type hints.",
            findings=[
                {
                    "type": "readability",
                    "severity": "medium",
                    "location": "function definition",
                    "description": "Missing type hints for arguments",
                    "suggestion": "Add type hints to make it clearer"
                }
            ],
            confidence=1.0,
            review_category="readability"
        )
        
        step_result = await env.step(action)
        
        print("Success! Received feedback from the remote environment.")
        print(f"Step Reward: {step_result.reward:.3f}")
        print(f"Cumulative Score: {step_result.observation.cumulative_score:.3f}")
        print(f"Feedback: {step_result.observation.feedback}")
        print(f"Episode Done: {step_result.done}")
        
    except Exception as e:
        print(f"\n[Error] Error communicating with Hugging Face Space: {e}")
        print("Note: If you just deployed, it might take a few minutes for the Space container to build and boot up.")
        print("Check the Space logs on Hugging Face for more details.")

def main():
    parser = argparse.ArgumentParser(description="Test CodeReviewEnv deployed on Hugging Face Spaces")
    parser.add_argument("repo_id", help="Your Hugging Face Space repo ID (e.g. 'username/code-review-env')")
    args = parser.parse_args()
    
    asyncio.run(test_deployment(args.repo_id))

if __name__ == "__main__":
    main()
