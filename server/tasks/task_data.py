"""
tasks/task_data.py - Sample Pull Requests for Code Review Tasks
===============================================================

This file contains SYNTHETIC data - fake PRs that we created ourselves.
We don't need real GitHub PRs because:
1. We control ground truth (know exactly what issues exist)
2. Reproducible every time
3. No IP/legal concerns
4. Can design for specific difficulty levels

LEARNING: Why Synthetic Data for RL?
In RL training, you want:
- Consistent evaluation (same PR = same answer needed)
- Known ground truth (we know what agent SHOULD find)
- Controllable difficulty (can make exactly easy/medium/hard)

Real data is messy - you'd need experts to annotate ground truth.
Synthetic data is clean - we define ground truth ourselves!

Each task has:
- pr_info: What the agent sees (code, title, description)
- ground_truth: What issues EXIST (hidden from agent)
- expected_findings: What agent SHOULD identify
"""

# =============================================================================
# TASK 1: READABILITY REVIEW (Easy)
# =============================================================================
# Task: Identify code style and readability issues
# Difficulty: Easy - issues are obvious, no logic analysis needed
# What agent learns: Basic code quality assessment

TASK1_READABILITY_PR = {
    "id": "readability_001",
    "title": "Add calculation utility function",
    "description": "Add helper function for basic math operations",
    "language": "python",
    "code": '''def calc(a,b):
    z=a+b
    return z

def mult(x,y):
    return x*y

def div(n,d):
    return n/d''',
    "files_changed": ["utils/math.py"],
    "issues": [
        {
            "type": "readability",
            "severity": "medium",
            "location": "function calc",
            "description": "Function name 'calc' is vague, should be descriptive",
            "suggestion": "Rename to 'calculate_sum'"
        },
        {
            "type": "readability", 
            "severity": "high",
            "location": "function calc",
            "description": "No docstring or doc comments",
            "suggestion": "Add a docstring explaining what the function does"
        },
        {
            "type": "readability",
            "severity": "medium",
            "location": "line 1",
            "description": "Variables 'a', 'b', 'z' are single letters - not descriptive",
            "suggestion": "Use meaningful names like 'first_number', 'second_number'"
        },
        {
            "type": "readability",
            "severity": "medium",
            "location": "function mult",
            "description": "No type hints for function parameters or return",
            "suggestion": "Add type hints: def mult(x: int, y: int) -> int"
        },
        {
            "type": "readability",
            "severity": "high",
            "location": "function div",
            "description": "Division by zero not handled",
            "suggestion": "Add check for d == 0 before division"
        },
    ]
}

TASK1_READABILITY_PR_2 = {
    "id": "readability_002",
    "title": "Process user data",
    "description": "Handle user registration data",
    "language": "python",
    "code": '''class user:
    def __init__(self,n,a,p):
        self.name=n
        self.age=a
        self.passwd=p
    def get(self):
        return self.name,self.age
    def set(self,n,a):
        self.name=n
        self.age=a''',
    "files_changed": ["models/user.py"],
    "issues": [
        {
            "type": "readability",
            "severity": "high",
            "location": "class user",
            "description": "Class name should be CapitalCase",
            "suggestion": "Rename to 'User'"
        },
        {
            "type": "readability",
            "severity": "high",
            "location": "parameters",
            "description": "Single letter parameters 'n', 'a', 'p' are unclear",
            "suggestion": "Use 'name', 'age', 'password'"
        },
        {
            "type": "readability",
            "severity": "medium",
            "location": "method get",
            "description": "'get' is too generic, doesn't indicate what it returns",
            "suggestion": "Rename to 'get_user_info' or 'get_profile'"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "class user",
            "description": "No class docstring",
            "suggestion": "Add docstring explaining the User class purpose"
        },
    ]
}

TASK1_PR_POOL = [TASK1_READABILITY_PR, TASK1_READABILITY_PR_2]


# =============================================================================
# TASK 2: BUG & LOGIC REVIEW (Medium)
# =============================================================================
# Task: Find logic errors and bugs in code
# Difficulty: Medium - requires understanding what code SHOULD do
# What agent learns: Critical thinking about program correctness

TASK2_BUG_LOGIC_PR = {
    "id": "bug_logic_001",
    "title": "Find maximum value in list",
    "description": "Algorithm to find the maximum value in a list of numbers",
    "language": "python",
    "code": '''def find_max(numbers):
    """Find the maximum value in a list."""
    max_val = 0
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val''',
    "files_changed": ["algorithms/max_value.py"],
    "issues": [
        {
            "type": "logic",
            "severity": "critical",
            "location": "line 3",
            "description": "Initializing max_val to 0 fails for lists with only negative numbers",
            "suggestion": "Initialize with float('-inf') or first element of list"
        },
        {
            "type": "logic",
            "severity": "high",
            "location": "line 6",
            "description": "Function will crash with empty list (UnboundLocalError)",
            "suggestion": "Add check for empty list and return None or raise exception"
        },
    ]
}

TASK2_BUG_LOGIC_PR_2 = {
    "id": "bug_logic_002",
    "title": "Check if string is palindrome",
    "description": "Verify if a string reads the same forwards and backwards",
    "language": "python",
    "code": '''def is_palindrome(s):
    """Check if string is a palindrome."""
    s = s.lower()
    s = s.replace(" ", "")
    return s == s[::-1]

def find_palindromes(words):
    results = []
    for word in words:
        if is_palindrome(word):
            results.append(word)
    return results''',
    "files_changed": ["utils/string_utils.py"],
    "issues": [
        {
            "type": "logic",
            "severity": "medium",
            "location": "is_palindrome, line 3",
            "description": "replace only handles space, not other punctuation",
            "suggestion": "Use regex to remove all non-alphanumeric characters"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "line 9",
            "description": "Could use list comprehension for conciseness",
            "suggestion": "return [w for w in words if is_palindrome(w)]"
        },
    ]
}

TASK2_BUG_LOGIC_PR_3 = {
    "id": "bug_logic_003",
    "title": "Calculate factorial",
    "description": "Calculate the factorial of a non-negative integer",
    "language": "python",
    "code": '''def factorial(n):
    """Calculate n! (factorial of n)."""
    if n < 0:
        return None
    result = 1
    for i in range(n):
        result = result * i
    return result''',
    "files_changed": ["math/factorial.py"],
    "issues": [
        {
            "type": "logic",
            "severity": "critical",
            "location": "line 5",
            "description": "Multiplication uses wrong variable - should be 'i+1' not 'i'",
            "suggestion": "result = result * (i + 1)"
        },
        {
            "type": "logic",
            "severity": "high",
            "location": "line 2",
            "description": "Should handle n=0 case (0! = 1)",
            "suggestion": "Add: if n == 0: return 1"
        },
    ]
}

TASK2_PR_POOL = [TASK2_BUG_LOGIC_PR, TASK2_BUG_LOGIC_PR_2, TASK2_BUG_LOGIC_PR_3]


# =============================================================================
# TASK 3: FULL PR REVIEW (Hard)
# =============================================================================
# Task: Comprehensive review of code + description accuracy
# Difficulty: Hard - requires security knowledge + verification
# What agent learns: Professional code review skills

TASK3_FULL_REVIEW_PR = {
    "id": "full_review_001",
    "title": "Add user authentication",
    "description": "Validates user credentials securely with password hashing",
    "language": "python",
    "code": '''from db import Database

def authenticate_user(username, password):
    """Authenticate user with username and password."""
    db = Database()
    
    # Get user from database
    query = f"SELECT * FROM users WHERE username='{username}'"
    user = db.execute(query)
    
    if not user:
        return False
    
    # Check password (stored as plain text)
    if user.password == password:
        return True
    
    return False

def create_session(user_id):
    """Create a new session for authenticated user."""
    import random
    session_id = random.randint(1000000, 9999999)
    return session_id''',
    "files_changed": ["auth/login.py", "auth/session.py"],
    "issues": [
        # SECURITY - Critical issues
        {
            "type": "security",
            "severity": "critical",
            "location": "line 9",
            "description": "SQL Injection vulnerability - user input directly in query",
            "suggestion": "Use parameterized queries: query = 'SELECT * FROM users WHERE username=?'"
        },
        {
            "type": "security",
            "severity": "critical",
            "location": "line 14",
            "description": "Password stored/compared as plain text - security risk",
            "suggestion": "Use password hashing (bcrypt, argon2) with hashing and salt"
        },
        {
            "type": "security",
            "severity": "high",
            "location": "function create_session",
            "description": "Session ID uses weak random - predictable",
            "suggestion": "Use secrets.token_hex() or uuid4() for secure session IDs"
        },
        # LOGIC issues
        {
            "type": "logic",
            "severity": "medium",
            "location": "line 14",
            "description": "Code returns True even if password is None/empty",
            "suggestion": "Add explicit check: if user.password and user.password == password"
        },
        # READABILITY issues
        {
            "type": "readability",
            "severity": "low",
            "location": "function authenticate_user",
            "description": "Function is doing two things (auth + db lookup)",
            "suggestion": "Split into separate functions or add docstring"
        },
        # DESCRIPTION MATCH - Critical!
        {
            "type": "description_match",
            "severity": "critical",
            "location": "overall",
            "description": "PR claims 'secure password hashing' but code has NO hashing",
            "suggestion": "Either add hashing or update description to match implementation"
        },
    ]
}

TASK3_FULL_REVIEW_PR_2 = {
    "id": "full_review_002",
    "title": "API endpoint for user registration",
    "description": "REST API endpoint to register new users with email verification",
    "language": "python",
    "code": '''from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Store directly in database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO users VALUES (?, ?, ?)",
        (username, email, password)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success"})

@app.route('/user/<username>')
def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    # Return user data including password (needed for auth)
    return jsonify({
        "username": user[0],
        "email": user[1],
        "password": user[2]  # Exposing password in API!
    })''',
    "files_changed": ["api/routes.py", "api/models.py"],
    "issues": [
        # SECURITY - Critical
        {
            "type": "security",
            "severity": "critical",
            "location": "function register",
            "description": "SQL Injection possible - using string formatting in query",
            "suggestion": "Already using parameterized queries correctly here - GOOD"
        },
        {
            "type": "security",
            "severity": "critical",
            "location": "line 40",
            "description": "PASSWORD EXPOSED IN API RESPONSE - major security breach",
            "suggestion": "Never return password hash in API response"
        },
        {
            "type": "security",
            "severity": "critical",
            "location": "function register",
            "description": "No password hashing - storing plain text passwords",
            "suggestion": "Hash password before storing: hash = bcrypt.hash(password)"
        },
        {
            "type": "security",
            "severity": "high",
            "location": "function register",
            "description": "No input validation - could register with empty/bad data",
            "suggestion": "Add validation for email format, password strength"
        },
        {
            "type": "security",
            "severity": "high",
            "location": "function register",
            "description": "No rate limiting - vulnerable to brute force registration",
            "suggestion": "Add rate limiting middleware"
        },
        # LOGIC issues
        {
            "type": "logic",
            "severity": "medium",
            "location": "function register",
            "description": "No check if username/email already exists - duplicate users possible",
            "suggestion": "Check for existing user before inserting"
        },
        {
            "type": "logic",
            "severity": "medium",
            "location": "function get_user",
            "description": "No null check for user - will crash if user doesn't exist",
            "suggestion": "Return 404 if user is None"
        },
        # DESCRIPTION MATCH
        {
            "type": "description_match",
            "severity": "critical",
            "location": "overall",
            "description": "PR claims 'email verification' but NO verification logic exists",
            "suggestion": "Add email verification flow or update description"
        },
    ]
}

TASK3_PR_POOL = [TASK3_FULL_REVIEW_PR, TASK3_FULL_REVIEW_PR_2]


# =============================================================================
# TASK POOL - All tasks organized by difficulty
# =============================================================================

# Easy tasks (readability only)
EASY_TASKS = [
    {"task_id": "readability", "pr": pr}
    for pr in TASK1_PR_POOL
]

# Medium tasks (bug/logic focus)
MEDIUM_TASKS = [
    {"task_id": "bug_logic", "pr": pr}
    for pr in TASK2_PR_POOL
]

# Hard tasks (full review)
HARD_TASKS = [
    {"task_id": "full_review", "pr": pr}
    for pr in TASK3_PR_POOL
]

# All tasks combined
ALL_TASKS = EASY_TASKS + MEDIUM_TASKS + HARD_TASKS


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_task_by_id(task_id: str, index: int = 0) -> dict:
    """
    Get a specific task by difficulty level.
    
    Args:
        task_id: One of 'readability', 'bug_logic', 'full_review'
        index: Which PR in that pool (for variety)
    
    Returns:
        Task dictionary with pr_info and ground_truth
    """
    pools = {
        "readability": TASK1_PR_POOL,
        "bug_logic": TASK2_PR_POOL,
        "full_review": TASK3_PR_POOL,
    }
    
    pool = pools.get(task_id, TASK1_PR_POOL)
    pr = pool[index % len(pool)]
    
    return {
        "task_id": task_id,
        "pr_info": {
            "title": pr["title"],
            "description": pr["description"],
            "language": pr["language"],
            "code": pr["code"],
            "files_changed": pr["files_changed"],
            "description_match": True  # Assume matches unless issues say otherwise
        },
        "ground_truth_issues": pr["issues"]
    }


def get_random_task(difficulty: str = None) -> dict:
    """
    Get a random task, optionally filtered by difficulty.
    
    Args:
        difficulty: 'easy', 'medium', 'hard', or None for random
    
    Returns:
        Random task dictionary
    """
    import random
    
    if difficulty == "easy":
        task_data = random.choice(EASY_TASKS)
    elif difficulty == "medium":
        task_data = random.choice(MEDIUM_TASKS)
    elif difficulty == "hard":
        task_data = random.choice(HARD_TASKS)
    else:
        task_data = random.choice(ALL_TASKS)
    
    return {
        "task_id": task_data["task_id"],
        "pr_info": {
            "title": task_data["pr"]["title"],
            "description": task_data["pr"]["description"],
            "language": task_data["pr"]["language"],
            "code": task_data["pr"]["code"],
            "files_changed": task_data["pr"]["files_changed"],
            "description_match": True
        },
        "ground_truth_issues": task_data["pr"]["issues"]
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TASK1_PR_POOL",
    "TASK2_PR_POOL", 
    "TASK3_PR_POOL",
    "EASY_TASKS",
    "MEDIUM_TASKS",
    "HARD_TASKS",
    "ALL_TASKS",
    "get_task_by_id",
    "get_random_task",
]
