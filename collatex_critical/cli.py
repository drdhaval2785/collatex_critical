import argparse
import os
from .collatex_critical import collatex_critical
from .generate import run_generate

def main():
    parser = argparse.ArgumentParser(prog="collatex-critical")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate
    p3 = subparsers.add_parser("generate", help="Full pipeline replacement for generate.sh")
    p3.add_argument("project_id", help="Usually the name of your project")
    p3.add_argument(
        "-t",
        "--transliterations",
        type=lambda s: s.split(","),  # comma-separated
        default=None,
        help="Comma-separated list of transliterations (default: devanagari,slp1,iast)",
    )

    args = parser.parse_args()

    if args.command == "generate":
        run_generate(args.project_id, translits=args.transliterations)
    else:
        print("Invalid usage. Try collatex-critical generate projectId")
