"""
Command-Line Interface for Harbor Task Generation Pipeline
Innodata AI Hackathon - pallets/click Pipeline
"""

import sys
import argparse
from pathlib import Path
from .config import TARGET_REPO_URL, DEFAULT_BASELINE_COMMIT, HARBOR_SCHEMA_VERSION
from .git_miner import ClickTaskCatalog
from .generator import TaskGenerator
from .linter import HarborLinter

def print_banner():
    print("=" * 65)
    print("   INNODATA AI HACKATHON: HARBOR TASK-GENERATION PIPELINE")
    print(f"   Target: pallets/click @ baseline {DEFAULT_BASELINE_COMMIT[:7]}")
    print(f"   Harbor Standard: v{HARBOR_SCHEMA_VERSION}")
    print("=" * 65)

def cmd_list(args):
    print_banner()
    tasks = ClickTaskCatalog.get_all_tasks()
    print(f"\nDiscovered {len(tasks)} verified reproducible tasks from pallets/click:\n")
    for i, t in enumerate(tasks, 1):
        print(f" [{i}] {t.metadata.name}")
        print(f"     Difficulty: {t.metadata.difficulty.upper()} | Issue: {t.metadata.issue_id}")
        print(f"     Summary:    {t.metadata.summary}")
        print(f"     Tags:       {', '.join(t.metadata.tags)}\n")

def cmd_generate_all(args):
    print_banner()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generator = TaskGenerator()
    linter = HarborLinter()
    tasks = ClickTaskCatalog.get_all_tasks()
    
    print(f"\n[PIPELINE] Generating {len(tasks)} containerized Harbor task packages in: {output_dir}\n")
    
    for task in tasks:
        task_dir = generator.generate(task, output_dir)
        print(f" -> Generated task package: {task_dir.name}")
        
        # Run Harbor v0.25 linter
        passed, errors, warnings = linter.lint_task(task_dir)
        if passed:
            print(f"    [LINTER PASS] Harbor v0.25.x standard confirmed.")
        else:
            print(f"    [LINTER FAIL] Errors: {errors}")
            
    print("\n[PIPELINE] Task generation and validation complete.")

def cmd_lint(args):
    print_banner()
    task_path = Path(args.path)
    linter = HarborLinter()
    
    print(f"\n[LINTER] Inspecting task package: {task_path}\n")
    passed, errors, warnings = linter.lint_task(task_path)
    
    if passed:
        print("  RESULT: PASSED (Harbor v0.25.x compliant)")
    else:
        print("  RESULT: FAILED")
        for err in errors:
            print(f"    - ERROR: {err}")
            
    for w in warnings:
        print(f"    - WARNING: {w}")
        
    return 0 if passed else 1

def main():
    parser = argparse.ArgumentParser(description="Harbor v0.25.x Task Generation Pipeline for pallets/click")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list
    subparsers.add_parser("list", help="List available tasks from pallets/click catalog")

    # generate-all
    gen_parser = subparsers.add_parser("generate-all", help="Generate all containerized Harbor task packages")
    gen_parser.add_argument("--output-dir", default="./tasks", help="Output directory for task packages")

    # lint
    lint_parser = subparsers.add_parser("lint", help="Lint a task package against Harbor v0.25.x specifications")
    lint_parser.add_argument("path", help="Path to task package directory")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "generate-all":
        cmd_generate_all(args)
    elif args.command == "lint":
        sys.exit(cmd_lint(args))
    else:
        # Default behavior: run generate-all
        args.output_dir = "./tasks"
        cmd_generate_all(args)

if __name__ == "__main__":
    main()
