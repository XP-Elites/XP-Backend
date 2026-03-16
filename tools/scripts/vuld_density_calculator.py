import json
import os
import sys
from pathlib import Path

from red_flag_functions import all_metrics


def run(directory: Path):
    # Calculate metrics for each Python file and store results
    results = {}
    for file in sorted(directory.rglob("*.py")):
        if not file.is_file():
            continue
        # Skip the results file itself if somehow present
        if file.name == "results.json":
            continue
        metrics = all_metrics(file)
        # Store path relative to /data for cleaner output
        relative_path = str(file.relative_to(directory))
        results[relative_path] = metrics
        print(f"{relative_path}: {metrics}")

    # Merge under "vuln_density" key, preserving any existing keys
    output_path = directory / "results.json"
    if output_path.exists():
        with open(output_path, "r") as f:
            existing = json.load(f)
    else:
        existing = {}

    existing["vuln_density"] = results

    with open(output_path, "w") as f:
        json.dump(existing, f, indent=4)
    print(f"Results saved to {output_path}")


def get_target_directory() -> Path:
    return Path(sys.argv[1] if len(sys.argv) > 1 else os.getenv("DATA_DIR", "/data"))


if __name__ == "__main__":
    run(get_target_directory())
