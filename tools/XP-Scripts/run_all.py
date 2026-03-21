import sys
from pathlib import Path

from CC_Calculator import run as run_cc
from vuld_density_calculator import run as run_vuln_density


def main():
    target_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/data")
    run_cc(target_dir)
    run_vuln_density(target_dir)


if __name__ == "__main__":
    main()