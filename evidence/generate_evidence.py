"""
Topic 6 evidence generator.

Creates deterministic evidence artifacts for:

- graph structure
- execution order
- branch and merge behavior
- paragraph analysis
- cycle rejection
- missing-dependency rejection
- test summary

All evidence uses synthetic local data.
No external APIs or credentials are used.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SRC_DIR = PROJECT_ROOT / "src"

# Allow imports from both:
#
#   src/
#   project root/
#
# This is necessary because this script is executed directly
# from the evidence directory.
for import_path in (
    SRC_DIR,
    PROJECT_ROOT,
):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))


from graph_of_thought import (  # noqa: E402
    build_graph,
    run_graph,
)

from thought_graph.cli import (  # noqa: E402
    analyze_paragraph,
)


# ---------------------------------------------------------------------------
# Evidence directories
# ---------------------------------------------------------------------------

EVIDENCE_DIR = PROJECT_ROOT / "evidence"

TRACES_DIR = (
    EVIDENCE_DIR / "traces"
)

SNAPSHOTS_DIR = (
    EVIDENCE_DIR / "state_snapshots"
)


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def write_json(
    path: Path,
    data: dict,
) -> None:
    """Write deterministic JSON evidence."""

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


# ---------------------------------------------------------------------------
# Graph structure evidence
# ---------------------------------------------------------------------------

def generate_graph_structure() -> None:
    """Capture the graph definition."""

    graph = build_graph()

    nodes = []

    for name, (
        dependencies,
        function,
    ) in graph.items():

        nodes.append(
            {
                "name": name,
                "dependencies": list(
                    dependencies
                ),
                "function": function.__name__,
            }
        )

    write_json(
        SNAPSHOTS_DIR
        / "graph_structure.json",
        {
            "assessment": (
                "Topic 6: Create an Executable "
                "Graph of Thought Workflow"
            ),
            "node_count": len(nodes),
            "nodes": nodes,
            "branch_structure": {
                "source": "split",
                "branches": [
                    "keywords",
                    "counts",
                ],
                "merge": "merge",
            },
        },
    )


# ---------------------------------------------------------------------------
# Execution evidence
# ---------------------------------------------------------------------------

def generate_execution_evidence() -> None:
    """Capture a normal graph execution."""

    graph = build_graph()

    trace: list[str] = []

    results = run_graph(
        graph,
        {
            "text": (
                "Agents plan tasks. "
                "Agents execute tasks."
            )
        },
        trace,
    )

    write_json(
        TRACES_DIR
        / "execution_trace.json",
        {
            "assessment": (
                "Topic 6: Create an Executable "
                "Graph of Thought Workflow"
            ),
            "input": {
                "text": (
                    "Agents plan tasks. "
                    "Agents execute tasks."
                )
            },
            "execution_order": trace,
            "node_count": len(trace),
            "result": results["merge"],
        },
    )


# ---------------------------------------------------------------------------
# Branch and merge evidence
# ---------------------------------------------------------------------------

def generate_branch_snapshots() -> None:
    """Capture both branch outputs and the merged result."""

    graph = build_graph()

    results = run_graph(
        graph,
        {
            "text": (
                "Agents plan tasks. "
                "Agents execute tasks."
            )
        },
    )

    write_json(
        SNAPSHOTS_DIR
        / "branch_outputs.json",
        {
            "split_output": results["split"],
            "keywords_branch": results["keywords"],
            "counts_branch": results["counts"],
            "merged_output": results["merge"],
        },
    )


# ---------------------------------------------------------------------------
# Paragraph analysis evidence
# ---------------------------------------------------------------------------

def generate_paragraph_analysis() -> None:
    """Capture the final paragraph analysis."""

    result = analyze_paragraph(
        "Agents plan tasks. "
        "Agents execute tasks."
    )

    write_json(
        TRACES_DIR
        / "paragraph_analysis.json",
        result,
    )


# ---------------------------------------------------------------------------
# Missing dependency evidence
# ---------------------------------------------------------------------------

def generate_missing_dependency_evidence() -> None:
    """Demonstrate safe rejection of a missing dependency."""

    graph = build_graph()

    graph["merge"] = (
        ["missing_node"],
        lambda data: data,
    )

    try:
        run_graph(
            graph,
            {
                "text": "Example.",
            },
        )

    except ValueError as error:

        write_json(
            TRACES_DIR
            / "missing_dependency_rejection.json",
            {
                "scenario": (
                    "missing dependency"
                ),
                "status": "rejected",
                "error_type": (
                    type(error).__name__
                ),
                "message": str(error),
            },
        )


# ---------------------------------------------------------------------------
# Cycle evidence
# ---------------------------------------------------------------------------

def generate_cycle_evidence() -> None:
    """Demonstrate safe rejection of a cyclic graph."""

    graph = {
        "a": (
            ["b"],
            lambda data: data,
        ),
        "b": (
            ["a"],
            lambda data: data,
        ),
    }

    try:
        run_graph(
            graph,
            {},
        )

    except ValueError as error:

        write_json(
            TRACES_DIR
            / "cycle_rejection.json",
            {
                "scenario": (
                    "two-node dependency cycle"
                ),
                "status": "rejected",
                "error_type": (
                    type(error).__name__
                ),
                "message": str(error),
            },
        )


# ---------------------------------------------------------------------------
# Test evidence
# ---------------------------------------------------------------------------

def generate_test_summary() -> None:
    """Run the complete regression suite."""

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    write_json(
        TRACES_DIR
        / "test_summary.json",
        {
            "command": (
                f"{sys.executable} -m pytest -q"
            ),
            "return_code": (
                completed.returncode
            ),
            "passed": (
                completed.returncode == 0
            ),
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        },
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Generate all Topic 6 evidence."""

    generate_graph_structure()

    generate_execution_evidence()

    generate_branch_snapshots()

    generate_paragraph_analysis()

    generate_missing_dependency_evidence()

    generate_cycle_evidence()

    generate_test_summary()

    print(
        "Topic 6 evidence generated successfully."
    )


if __name__ == "__main__":
    main()