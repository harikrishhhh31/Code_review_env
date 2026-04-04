
                                                                               
         
                                                                               

from typing import Optional

                                                                               
                                   
                                                                               
                                                  
                                                                 
                                                  

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

TASK1_READABILITY_PR_3 = {
    "id": "readability_003",
    "title": "Add temperature converter",
    "description": "Utility for converting between Fahrenheit and Celsius",
    "language": "python",
    "code": '''def conv(f):
    c=(f-32)*5/9
    return c

def conv2(c):
    return (c*9/5)+32''',
    "files_changed": ["utils/temperature.py"],
    "issues": [
        {
            "type": "readability",
            "severity": "medium",
            "location": "function conv",
            "description": "Function name 'conv' is vague",
            "suggestion": "Rename to 'fahrenheit_to_celsius'"
        },
        {
            "type": "readability",
            "severity": "medium",
            "location": "function conv2",
            "description": "Function name 'conv2' is vague",
            "suggestion": "Rename to 'celsius_to_fahrenheit'"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "line 1",
            "description": "No type hints",
            "suggestion": "Add type hints for parameters and return"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "functions conv/conv2",
            "description": "No docstrings",
            "suggestion": "Add docstrings describing conversions"
        },
    ]
}

TASK1_READABILITY_PR_4 = {
    "id": "readability_004",
    "title": "Format user name",
    "description": "Format first and last name into display name",
    "language": "javascript",
    "code": '''function fmt(a,b){
  return a+" "+b;
}

function n(x){
  return x.trim();
}''',
    "files_changed": ["src/user/format.js"],
    "issues": [
        {
            "type": "readability",
            "severity": "high",
            "location": "function fmt",
            "description": "Function name 'fmt' is unclear",
            "suggestion": "Rename to 'formatDisplayName'"
        },
        {
            "type": "readability",
            "severity": "high",
            "location": "function n",
            "description": "Function name 'n' is unclear",
            "suggestion": "Rename to 'normalizeName'"
        },
        {
            "type": "readability",
            "severity": "medium",
            "location": "line 1",
            "description": "No input validation for null or undefined",
            "suggestion": "Add checks for empty inputs"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "functions fmt/n",
            "description": "No JSDoc comments",
            "suggestion": "Add JSDoc comments for parameters"
        },
    ]
}

TASK1_READABILITY_PR_5 = {
    "id": "readability_005",
    "title": "Normalize emails",
    "description": "Utility to normalize email strings",
    "language": "python",
    "code": '''def norm_email(e):
    return e.strip().lower()

def norm_all(l):
    out = []
    for i in l:
        out.append(norm_email(i))
    return out''',
    "files_changed": ["utils/email.py"],
    "issues": [
        {
            "type": "readability",
            "severity": "medium",
            "location": "function norm_email",
            "description": "Function name is abbreviated",
            "suggestion": "Rename to 'normalize_email'"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "function norm_all",
            "description": "Variable name 'l' is unclear",
            "suggestion": "Use 'emails' instead of 'l'"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "function norm_all",
            "description": "List comprehension would be clearer",
            "suggestion": "Use: return [normalize_email(e) for e in emails]"
        },
    ]
}

TASK1_READABILITY_PR_6 = {
    "id": "readability_006",
    "title": "Capitalize product name",
    "description": "Utility to normalize product names",
    "language": "typescript",
    "code": '''export function cap(n){
  return n[0].toUpperCase()+n.slice(1);
}

export function clean(s){
  return s.trim();
}''',
    "files_changed": ["src/catalog/format.ts"],
    "issues": [
        {
            "type": "readability",
            "severity": "high",
            "location": "function cap",
            "description": "Function name 'cap' is unclear",
            "suggestion": "Rename to 'capitalizeName'"
        },
        {
            "type": "readability",
            "severity": "medium",
            "location": "function cap",
            "description": "No input validation for empty string",
            "suggestion": "Handle empty or null input"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "functions cap/clean",
            "description": "Missing type annotations",
            "suggestion": "Add explicit parameter and return types"
        },
    ]
}

TASK1_READABILITY_PR_7 = {
    "id": "readability_007",
    "title": "Normalize phone numbers",
    "description": "Strip punctuation from phone strings",
    "language": "python",
    "code": '''def normalize(p):
    return p.replace("-", "").replace("(", "").replace(")", "")

def normalize_all(items):
    res = []
    for i in items:
        res.append(normalize(i))
    return res''',
    "files_changed": ["utils/phone.py"],
    "issues": [
        {
            "type": "readability",
            "severity": "medium",
            "location": "function normalize",
            "description": "Function name is too generic",
            "suggestion": "Rename to 'normalize_phone'"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "line 1",
            "description": "Chained replace calls reduce readability",
            "suggestion": "Use regex or a helper function"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "function normalize_all",
            "description": "List comprehension would be clearer",
            "suggestion": "Use: return [normalize_phone(i) for i in items]"
        },
    ]
}

TASK1_PR_POOL = [
    TASK1_READABILITY_PR,
    TASK1_READABILITY_PR_2,
    TASK1_READABILITY_PR_3,
    TASK1_READABILITY_PR_4,
    TASK1_READABILITY_PR_5,
    TASK1_READABILITY_PR_6,
    TASK1_READABILITY_PR_7,
]


                                                                               
                                     
                                                                               
                                          
                                                                 
                                                                

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

TASK2_BUG_LOGIC_PR_4 = {
    "id": "bug_logic_004",
    "title": "Calculate average",
    "description": "Compute average for list of numbers",
    "language": "javascript",
    "code": '''function average(nums){
  let total = 0;
  for (let i = 0; i < nums.length; i++) {
    total += nums[i];
  }
  return total / nums.length;
}''',
    "files_changed": ["src/math/average.js"],
    "issues": [
        {
            "type": "logic",
            "severity": "high",
            "location": "function average",
            "description": "No check for empty array; division by zero returns Infinity",
            "suggestion": "Handle empty array and return null or 0"
        },
    ]
}

TASK2_BUG_LOGIC_PR_5 = {
    "id": "bug_logic_005",
    "title": "Filter active users",
    "description": "Return only active users from list",
    "language": "python",
    "code": '''def active_users(users):
    """Return only active users."""
    result = []
    for u in users:
        if u.get("active") == True:
            result.append(u)
    return users''',
    "files_changed": ["users/filters.py"],
    "issues": [
        {
            "type": "logic",
            "severity": "critical",
            "location": "line 6",
            "description": "Returns original users list instead of filtered result",
            "suggestion": "Return result instead of users"
        },
    ]
}

TASK2_BUG_LOGIC_PR_6 = {
    "id": "bug_logic_006",
    "title": "Sum order totals",
    "description": "Calculate total price from list of items",
    "language": "python",
    "code": '''def total(items):
    """Sum prices from list of items."""
    total = 0
    for item in items:
        total = item["price"]
    return total''',
    "files_changed": ["orders/totals.py"],
    "issues": [
        {
            "type": "logic",
            "severity": "high",
            "location": "line 4",
            "description": "Overwrites total instead of accumulating",
            "suggestion": "Use total += item['price']"
        },
    ]
}

TASK2_BUG_LOGIC_PR_7 = {
    "id": "bug_logic_007",
    "title": "Compute discount",
    "description": "Apply percentage discount to a price",
    "language": "typescript",
    "code": '''export function discount(price: number, pct: number){
  return price - price * pct;
}''',
    "files_changed": ["src/billing/discount.ts"],
    "issues": [
        {
            "type": "logic",
            "severity": "medium",
            "location": "function discount",
            "description": "Assumes pct is 0-1, but callers may pass 10 for 10%",
            "suggestion": "Clarify percent units or divide by 100"
        },
    ]
}

TASK2_PR_POOL = [
    TASK2_BUG_LOGIC_PR,
    TASK2_BUG_LOGIC_PR_2,
    TASK2_BUG_LOGIC_PR_3,
    TASK2_BUG_LOGIC_PR_4,
    TASK2_BUG_LOGIC_PR_5,
    TASK2_BUG_LOGIC_PR_6,
    TASK2_BUG_LOGIC_PR_7,
]


                                                                               
                               
                                                                               
                                                           
                                                               
                                                    

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
                      
        {
            "type": "logic",
            "severity": "medium",
            "location": "line 14",
            "description": "Code returns True even if password is None/empty",
            "suggestion": "Add explicit check: if user.password and user.password == password"
        },
                            
        {
            "type": "readability",
            "severity": "low",
            "location": "function authenticate_user",
            "description": "Function is doing two things (auth + db lookup)",
            "suggestion": "Split into separate functions or add docstring"
        },
                                       
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
                           
        {
            "type": "description_match",
            "severity": "critical",
            "location": "overall",
            "description": "PR claims 'email verification' but NO verification logic exists",
            "suggestion": "Add email verification flow or update description"
        },
    ]
}

TASK3_FULL_REVIEW_PR_3 = {
    "id": "full_review_003",
    "title": "Add password reset endpoint",
    "description": "Allows users to reset password with secure token validation",
    "language": "javascript",
    "code": '''const express = require("express");
const app = express();

app.post("/reset", (req, res) => {
  const token = req.body.token;
  const newPassword = req.body.password;

  // TODO: validate token
  if (!token) {
    return res.status(400).send("missing token");
  }

  // directly update password
  db.query(`UPDATE users SET password='${newPassword}' WHERE reset_token='${token}'`);
  return res.send("ok");
});''',
    "files_changed": ["api/reset.js"],
    "issues": [
        {
            "type": "security",
            "severity": "critical",
            "location": "db.query line",
            "description": "SQL injection via string interpolation",
            "suggestion": "Use parameterized queries"
        },
        {
            "type": "security",
            "severity": "critical",
            "location": "password update",
            "description": "Stores password in plain text",
            "suggestion": "Hash password before storing"
        },
        {
            "type": "logic",
            "severity": "high",
            "location": "token validation",
            "description": "Token is not validated or expired; TODO left",
            "suggestion": "Validate token and check expiration"
        },
        {
            "type": "description_match",
            "severity": "critical",
            "location": "overall",
            "description": "PR claims secure token validation but none implemented",
            "suggestion": "Implement token validation or update description"
        },
    ]
}

TASK3_FULL_REVIEW_PR_4 = {
    "id": "full_review_004",
    "title": "Add API key authentication",
    "description": "Validate API key on protected endpoints",
    "language": "python",
    "code": '''from flask import request

def require_key(func):
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-KEY")
        if key != "hardcoded":
            return {"error": "unauthorized"}, 401
        return func(*args, **kwargs)
    return wrapper''',
    "files_changed": ["auth/api_key.py"],
    "issues": [
        {
            "type": "security",
            "severity": "critical",
            "location": "line 5",
            "description": "Hardcoded API key in source code",
            "suggestion": "Load API key from secure config or environment"
        },
        {
            "type": "security",
            "severity": "high",
            "location": "line 4",
            "description": "No constant-time comparison for API key",
            "suggestion": "Use hmac.compare_digest for comparison"
        },
        {
            "type": "readability",
            "severity": "low",
            "location": "function require_key",
            "description": "Missing wraps decorator for function metadata",
            "suggestion": "Use functools.wraps"
        },
        {
            "type": "description_match",
            "severity": "medium",
            "location": "overall",
            "description": "PR claims protected endpoints but no routing shown",
            "suggestion": "Show how decorator is applied or update description"
        },
    ]
}

TASK3_FULL_REVIEW_PR_5 = {
    "id": "full_review_005",
    "title": "Add file upload endpoint",
    "description": "Upload profile images with validation",
    "language": "javascript",
    "code": '''app.post("/upload", (req, res) => {
  const file = req.files.file;
  const name = file.name;

  if (!name.endsWith(".png")) {
    return res.status(400).send("invalid");
  }

  file.mv("/uploads/" + name);
  return res.send("ok");
});''',
    "files_changed": ["api/upload.js"],
    "issues": [
        {
            "type": "security",
            "severity": "critical",
            "location": "file.mv",
            "description": "Path traversal risk with untrusted filename",
            "suggestion": "Sanitize filename or generate a safe name"
        },
        {
            "type": "security",
            "severity": "high",
            "location": "line 2",
            "description": "No file size limit or content-type validation",
            "suggestion": "Validate size and content type"
        },
        {
            "type": "logic",
            "severity": "medium",
            "location": "extension check",
            "description": "Only checks .png extension; content may be non-image",
            "suggestion": "Validate mime type and file signature"
        },
        {
            "type": "description_match",
            "severity": "medium",
            "location": "overall",
            "description": "PR claims validation but only checks extension",
            "suggestion": "Add full validation or update description"
        },
    ]
}

TASK3_PR_POOL = [
    TASK3_FULL_REVIEW_PR,
    TASK3_FULL_REVIEW_PR_2,
    TASK3_FULL_REVIEW_PR_3,
    TASK3_FULL_REVIEW_PR_4,
    TASK3_FULL_REVIEW_PR_5,
]


                                                                               
                                               
                                                                               

                               
EASY_TASKS = [
    {"task_id": "readability", "pr": pr}
    for pr in TASK1_PR_POOL
]

                                
MEDIUM_TASKS = [
    {"task_id": "bug_logic", "pr": pr}
    for pr in TASK2_PR_POOL
]

                          
HARD_TASKS = [
    {"task_id": "full_review", "pr": pr}
    for pr in TASK3_PR_POOL
]

                    
ALL_TASKS = EASY_TASKS + MEDIUM_TASKS + HARD_TASKS


                                                                               
                  
                                                                               

def get_task_by_id(task_id: str, index: int = 0) -> dict:
    pools = {
        "readability": TASK1_PR_POOL,
        "bug_logic": TASK2_PR_POOL,
        "full_review": TASK3_PR_POOL,
    }
    
    pool = pools.get(task_id, TASK1_PR_POOL)
    pr = pool[index % len(pool)]
    
    issues = pr["issues"]
    description_match = not any(
        issue.get("type") == "description_match" for issue in issues
    )

    return {
        "task_id": task_id,
        "pr_info": {
            "title": pr["title"],
            "description": pr["description"],
            "language": pr["language"],
            "code": pr["code"],
            "files_changed": pr["files_changed"],
            "description_match": description_match
        },
        "ground_truth_issues": issues
    }


def get_random_task(difficulty: Optional[str] = None) -> dict:
    import random
    
    if difficulty == "easy":
        task_data = random.choice(EASY_TASKS)
    elif difficulty == "medium":
        task_data = random.choice(MEDIUM_TASKS)
    elif difficulty == "hard":
        task_data = random.choice(HARD_TASKS)
    else:
        task_data = random.choice(ALL_TASKS)
    
    issues = task_data["pr"]["issues"]
    description_match = not any(
        issue.get("type") == "description_match" for issue in issues
    )

    return {
        "task_id": task_data["task_id"],
        "pr_info": {
            "title": task_data["pr"]["title"],
            "description": task_data["pr"]["description"],
            "language": task_data["pr"]["language"],
            "code": task_data["pr"]["code"],
            "files_changed": task_data["pr"]["files_changed"],
            "description_match": description_match
        },
        "ground_truth_issues": issues
    }


                                                                               
         
                                                                               

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
