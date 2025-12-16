import subprocess
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
STATE_DIR = PROJECT_ROOT / "runs"



def run_cli():
    cmd = ["python", "cli.py", "coder", "write hello world"]
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Run completed" in result.stdout
    return result.stdout


def find_latest_run():
    if not STATE_DIR.exists():
        raise AssertionError(f"State directory not found: {STATE_DIR}")

    runs = [p for p in STATE_DIR.iterdir() if p.is_dir()]
    assert runs, "No runs found in state/runs"

    runs.sort(key=lambda p: p.stat().st_mtime)
    return runs[-1]



def check_run_artifacts(run_dir: Path):
    input_file = run_dir / "input.json"
    output_file = run_dir / "output.json"
    log_file = run_dir / "trace.log"


    assert input_file.exists(), "input.json missing"
    assert output_file.exists(), "output.json missing"
    assert log_file.exists(), "log.txt missing"

    with output_file.open() as f:
        data = json.load(f)
        assert "agent_id" in data or "message" in data


def main():
    print("[TEST] running CLI")
    run_cli()

    print("[TEST] locating run")
    run_dir = find_latest_run()
    print(f"[TEST] run dir: {run_dir.name}")

    print("[TEST] checking artifacts")
    check_run_artifacts(run_dir)

    print("[OK] ALL TESTS PASSED")


if __name__ == "__main__":
    main()
