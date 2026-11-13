import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from config.settings import get_settings  # noqa: E402
from consumer360.pipeline import run_pipeline  # noqa: E402


def _maybe_run_dbt(skip: bool) -> None:
    if skip:
        return
    dbt_dir = ROOT / "dbt"
    for cmd in (["deps"], ["seed", "--full-refresh"], ["run"], ["test"]):
        subprocess.check_call(["dbt", *cmd], cwd=dbt_dir)


def main() -> None:
    parser = argparse.ArgumentParser(prog="consumer360")
    sub = parser.add_subparsers(dest="command", required=True)

    pipe = sub.add_parser("pipeline", help="Load bronze, build silver/gold, optional dbt")
    pipe.add_argument("--skip-dbt", action="store_true", help="Skip dbt (Python builds gold)")
    pipe.add_argument("--profiles", type=int, default=None, help="Regenerate synthetic data first")
    pipe.add_argument("--data-dir", type=Path, default=None)

    args = parser.parse_args()
    if args.command == "pipeline":
        if args.profiles is not None:
            subprocess.check_call(
                [sys.executable, str(ROOT / "data" / "synthetic" / "generate.py"), str(args.profiles)],
                cwd=str(ROOT),
            )
        if args.data_dir is not None:
            os.environ["CONSUMER360_DATA_DIR"] = str(args.data_dir)
        run_pipeline(get_settings())
        _maybe_run_dbt(args.skip_dbt)
        dq = ROOT / "data_quality" / "run_checks.py"
        if dq.exists():
            subprocess.check_call([sys.executable, str(dq)], cwd=str(ROOT))


if __name__ == "__main__":
    main()
