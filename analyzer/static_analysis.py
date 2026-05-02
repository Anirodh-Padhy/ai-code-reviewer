import ast

# ================= STATIC ANALYSIS =================
def analyze_code(code):
    issues = []

    try:
        tree = ast.parse(code)
    except Exception as e:
        return ["Syntax Error: " + str(e)]

    # 🔍 Long functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if len(node.body) > 20:
                issues.append(f"Function '{node.name}' is too long")

    # 🔍 Too many variables
    variables = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            variables.add(node.id)

    if len(variables) > 20:
        issues.append("Too many variables used")

    return issues


# ================= RULE-BASED SCORING =================
def calculate_rule_score(code):

    score = 10

    lines = code.split("\n")

    if len(lines) > 200:
        score -= 2

    if code.count("=") > 30:
        score -= 2

    if "try" not in code:
        score -= 2

    if "def " not in code:
        score -= 2

    return max(score, 1)