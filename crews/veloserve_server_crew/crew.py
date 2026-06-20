from pathlib import Path
import sys


BASE = Path.home() / "Projects" / "veloserve-ai"
sys.path.append(str(BASE / "crews"))

from _shared.runner import run_from_crew_dir


CREW_DIR = BASE / "crews" / "veloserve_server_crew"


if __name__ == "__main__":
    out = run_from_crew_dir(CREW_DIR)
    print(f"\nReport written to: {out}")
