import json
import os
import sys
from pathlib import Path

from cc_functions import calculate_cyclomatic_complexity, calculate_total_complexity


def run(directory: Path):
    # Calculate Cyclomatic Complexity for each Python file
    cc_results = {}
    for file in sorted(directory.rglob("*.py")):
        if not file.is_file():
            continue
        if file.name == "results.json":
            continue
        complexity = calculate_cyclomatic_complexity(file)
        relative_path = str(file.relative_to(directory))
        cc_results[relative_path] = complexity
        print(f"{relative_path}: {complexity}")

    total_complexity = calculate_total_complexity(directory)
    print(f"Total Cyclomatic Complexity: {total_complexity}")
    cc_results["total"] = total_complexity

    # Merge under "cyclomatic_complexity" key, preserving any existing keys
    output_path = directory / "results.json"
    if output_path.exists():
        with open(output_path, "r") as f:
            existing = json.load(f)
    else:
        existing = {}

    existing["cyclomatic_complexity"] = cc_results

    with open(output_path, "w") as f:
        json.dump(existing, f, indent=4)
    print(f"Results saved to {output_path}")


def get_target_directory() -> Path:
    return Path(sys.argv[1] if len(sys.argv) > 1 else os.getenv("DATA_DIR", "/data"))


if __name__ == "__main__":
    run(get_target_directory())
