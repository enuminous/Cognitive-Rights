"""python -m cognitive_rights demo | verify FILE --trusted-digest HASH"""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess

from .consent import ConsentEngine, verify, POLICY

ROOT = Path(__file__).resolve().parent.parent


def source_manifest():
    files = sorted(p for folder in ("cognitive_rights", "tests", "examples")
                   for p in (ROOT / folder).rglob("*")
                   if p.is_file() and p.suffix in (".py", ".json"))
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo")
    demo.add_argument("--output", default="artifacts")
    check = commands.add_parser("verify")
    check.add_argument("file")
    check.add_argument("--trusted-digest")
    args = parser.parse_args()
    if args.command == "verify":
        try:
            result = verify(json.loads(Path(args.file).read_text()), args.trusted_digest)
        except (ValueError, OSError) as error:
            result = {"verdict": "FAIL", "reason": str(error)}
        print(json.dumps(result, indent=2))
        return {"PASS": 0, "FAIL": 1, "UNRESOLVED": 2}[result["verdict"]]

    cases = json.loads((ROOT / "examples/consent_lifecycle.json").read_text())
    engine = ConsentEngine()
    results = []
    for case in cases:
        record = engine.apply(case["event"])
        ok = [record["decision"], record["reason"]] == case["expected"]
        results.append({"id": case["id"], "verdict": "PASS" if ok else "FAIL",
                        "expected": case["expected"], "observed": [record["decision"], record["reason"]]})
    package = engine.package()
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit, dirty = None, True
    report = {"policy": POLICY, "python": platform.python_version(), "source_commit": commit,
              "working_tree_dirty": dirty, "source_sha256": source_manifest(),
              "synthetic": True, "cases": results,
              "verdict": "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL",
              "package_hash": package["package_hash"],
              "limits": "Local policy simulation only. No identity authentication, external actions, sentience test or legal determination."}
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    for name, value in (("evidence.json", package), ("report.json", report)):
        (output / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    (output / "trusted-digest.txt").write_text(package["package_hash"] + "\n")
    print(json.dumps({"verdict": report["verdict"], "cases": len(results), "output": str(output)}, indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
