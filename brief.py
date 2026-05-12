#!/usr/bin/env python3
"""Daily news brief: fetch, curate, summarize, comment, assemble."""
from newsaggro.pipeline import run_pipeline
from newsaggro.output import save_brief


def main():
    print("Fetching, curating, summarizing, commenting...")
    markdown = run_pipeline()
    path = save_brief(markdown)
    print(f"\nBrief written to: {path}")


if __name__ == "__main__":
    main()
