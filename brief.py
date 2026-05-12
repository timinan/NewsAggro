#!/usr/bin/env python3
"""CLI entrypoint: run the pipeline and save the rendered brief."""
from newsaggro.pipeline import run_pipeline
from newsaggro.output import save_brief_html
from newsaggro.renderer import render_html


def main():
    print("Fetching, curating, summarizing...")
    result = run_pipeline()
    html = render_html(
        stories=result["stories"],
        date_str=result["date"],
        intro=result["intro"],
    )
    html_path, index_path = save_brief_html(html)
    print(f"\nHTML brief: {html_path}")
    print(f"Latest:     {index_path}")
    print(f"\nOpen with: open {index_path}")


if __name__ == "__main__":
    main()
