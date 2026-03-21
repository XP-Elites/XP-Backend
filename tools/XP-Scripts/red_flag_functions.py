import ast

def count_lines_of_code(source_code):
    count = 0
    for line in source_code.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            count += 1
    return count


def count_import_statements(node):
    count = 0
    for child in ast.walk(node):
        if isinstance(child, (ast.Import, ast.ImportFrom)):
            count += 1
    return count

def count_function_parameters(node):
    count = 0
    for child in ast.walk(node):
        if isinstance(child, ast.FunctionDef):
            count += len(child.args.args)
    return count

def count_function_lines(node):
    count = 0
    for child in ast.walk(node):
        if isinstance(child, ast.FunctionDef):
            count += len(child.body)
    return count

def all_metrics(file_path):
    with open(file_path, "r") as file:
        source_code = file.read()
        tree = ast.parse(source_code)

    loc = count_lines_of_code(source_code)
    imports = count_import_statements(tree)
    parameters = count_function_parameters(tree)
    function_lines = count_function_lines(tree)

    return {
        "lines_of_code": loc,
        "import_statements": imports,
        "function_parameters": parameters,
        "function_lines": function_lines
    }
