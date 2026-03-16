import ast

# Function to count Decision Points
def count_dps(node):
    decision_points = (
        ast.If,
        ast.For,
        ast.While,
        ast.With,
        ast.Try,
        ast.BoolOp,
        ast.ExceptHandler,
        ast.Match  # Match was added in Python 3.10
    )

    count = 0
    for child in ast.walk(node):
        if isinstance(child, decision_points):
            count += 1

    return count


# Function to calculate Cyclomatic Complexity for a single file
def calculate_cyclomatic_complexity(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())

    complexity = 1 + count_dps(tree)
    return complexity


# Function to calculate total Cyclomatic Complexity across a directory
def calculate_total_complexity(directory):
    total_complexity = 0
    for file in directory.rglob("*.py"):
        if not file.is_file():
            continue
        complexity = calculate_cyclomatic_complexity(file)
        total_complexity += complexity
    return total_complexity
