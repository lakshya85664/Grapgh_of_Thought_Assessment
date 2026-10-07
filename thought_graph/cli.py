"""
CLI for the Topic 6 Graph of Thought paragraph analysis.

The CLI uses the executable graph implemented in
src.graph_of_thought.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from graph_of_thought import build_graph, run_graph


def analyze_paragraph(text: str) -> dict:
    """
    Analyze a paragraph using the Graph of Thought workflow.

    Returns structured information from the graph, including:

    - normalized text
    - sentences
    - keywords
    - sentence count
    - merged analysis
    - execution trace
    """

    if not isinstance(text, str):
        raise TypeError(
            "text must be a string"
        )

    if not text.strip():
        raise ValueError(
            "text must not be empty"
        )

    graph = build_graph()

    trace: list[str] = []

    results = run_graph(
        graph,
        {
            "text": text,
        },
        trace,
    )

    return {
        "input": {
            "text": text,
        },
        "analysis": {
            "normalized_text": (
                results["normalize"]["text"]
            ),
            "sentences": (
                results["split"]["sentences"]
            ),
            "keywords": (
                results["keywords"]["keywords"]
            ),
            "sentence_count": (
                results["counts"]["counts"]
            ),
            "merged": results["merge"],
        },
        "execution": {
            "order": trace,
            "node_count": len(trace),
        },
    }


def _load_input(path: Path) -> dict:
    """Load and validate the JSON input file."""

    if not path.exists():
        raise FileNotFoundError(
            f"input file does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"input path is not a file: {path}"
        )

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"invalid JSON input: {error}"
        ) from error

    if not isinstance(data, dict):
        raise ValueError(
            "input JSON must contain an object"
        )

    if "text" not in data:
        raise ValueError(
            "input JSON must contain a 'text' field"
        )

    if not isinstance(data["text"], str):
        raise TypeError(
            "input 'text' must be a string"
        )

    return data


def _write_output(
    path: Path,
    data: dict,
) -> None:
    """Write structured JSON output."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def main() -> int:
    """Run the command-line interface."""

    parser = argparse.ArgumentParser(
        description=(
            "Topic 6 Graph of Thought "
            "paragraph analysis"
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="analyze a paragraph",
    )

    analyze_parser.add_argument(
        "--input",
        required=True,
        help="path to the input JSON file",
    )

    analyze_parser.add_argument(
        "--output",
        required=True,
        help="path for the output JSON file",
    )

    args = parser.parse_args()

    try:
        input_path = Path(args.input)
        output_path = Path(args.output)

        data = _load_input(
            input_path
        )

        result = analyze_paragraph(
            data["text"]
        )

        _write_output(
            output_path,
            result,
        )

        print(
            "Paragraph analysis written to "
            f"{output_path}"
        )

        print(
            "Execution order: "
            f"{result['execution']['order']}"
        )

        print(
            "Sentence count: "
            f"{result['analysis']['sentence_count']}"
        )

        print(
            "Keywords: "
            f"{result['analysis']['keywords']}"
        )

        return 0

    except (
        FileNotFoundError,
        TypeError,
        ValueError,
    ) as error:

        print(
            f"Error: {error}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )