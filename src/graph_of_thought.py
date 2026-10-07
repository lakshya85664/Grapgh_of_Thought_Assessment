"""
Topic 6: Create an Executable Graph of Thought Workflow.

This module implements Tasks 1–4 of the assessment.

Graph structure:

read
  |
  v
normalize
  |
  v
split
  |
  +----> keywords
  |
  +----> counts
          |
          v
        merge

Tasks implemented:

Task 1:
    Define a graph with six nodes and two branches that merge.

Task 2:
    Execute nodes in dependency order using run_graph().

Task 3:
    Merge the outputs of the keywords and counts branches.

Task 4:
    Detect missing dependencies and dependency cycles safely.

The implementation is deterministic, local, and does not use
external APIs or credentials.
"""

from __future__ import annotations

from collections.abc import Callable


NodeFunction = Callable[[dict], dict]
GraphDefinition = dict[str, tuple[list[str], NodeFunction]]


# ---------------------------------------------------------------------------
# Task 1 — Graph node functions
# ---------------------------------------------------------------------------

def _read(data: dict) -> dict:
    """Read the source text from the input."""

    return {
        "text": data["text"],
    }


def _normalize(data: dict) -> dict:
    """Normalize the input text."""

    return {
        "text": data["text"].strip(),
    }


def _split(data: dict) -> dict:
    """Split normalized text into sentences."""

    text = data["text"]

    sentences = [
        sentence.strip()
        for sentence in text.split(".")
        if sentence.strip()
    ]

    return {
        "sentences": sentences,
    }


def _keywords(data: dict) -> dict:
    """Extract a deterministic list of keywords."""

    sentences = data["sentences"]

    words = []

    for sentence in sentences:
        for word in sentence.split():
            cleaned = word.strip(".,!?;:").lower()

            if cleaned:
                words.append(cleaned)

    return {
        "keywords": words[:5],
    }


def _counts(data: dict) -> dict:
    """Count the number of sentences."""

    return {
        "counts": len(data["sentences"]),
    }


# ---------------------------------------------------------------------------
# Task 3 — Merge strategy
# ---------------------------------------------------------------------------

def _merge(data: dict) -> dict:
    """
    Merge the outputs of the keywords and counts branches.

    Required inputs:

        keywords -> list[str]
        counts   -> int

    Returns one structured result containing both values.
    """

    if "keywords" not in data:
        raise ValueError(
            "merge requires the 'keywords' branch output"
        )

    if "counts" not in data:
        raise ValueError(
            "merge requires the 'counts' branch output"
        )

    if not isinstance(data["keywords"], list):
        raise TypeError(
            "merge expects 'keywords' to be a list"
        )

    if not isinstance(data["counts"], int):
        raise TypeError(
            "merge expects 'counts' to be an integer"
        )

    return {
        "keywords": list(data["keywords"]),
        "sentences": data["counts"],
    }


# ---------------------------------------------------------------------------
# Task 1 — Graph definition
# ---------------------------------------------------------------------------

def build_graph() -> GraphDefinition:
    """
    Build and return the six-node Graph of Thought definition.

    Graph:

        read
          |
          v
        normalize
          |
          v
        split
          |
          +----> keywords
          |
          +----> counts
                  |
                  v
                merge

    The keywords and counts branches both depend on split.
    The merge node depends on both branches.
    """

    return {
        "read": (
            [],
            _read,
        ),

        "normalize": (
            ["read"],
            _normalize,
        ),

        "split": (
            ["normalize"],
            _split,
        ),

        "keywords": (
            ["split"],
            _keywords,
        ),

        "counts": (
            ["split"],
            _counts,
        ),

        "merge": (
            ["keywords", "counts"],
            _merge,
        ),
    }


# ---------------------------------------------------------------------------
# Task 4 — Graph validation
# ---------------------------------------------------------------------------

def _validate_graph(
    graph: GraphDefinition,
) -> None:
    """
    Validate graph structure and dependency references.

    Checks:

    - graph is a dictionary
    - node names are strings
    - node definitions are valid tuples
    - dependencies are lists
    - dependency names are strings
    - node functions are callable
    - every dependency exists in the graph
    """

    if not isinstance(graph, dict):
        raise TypeError(
            "graph must be a dictionary"
        )

    for name, definition in graph.items():

        if not isinstance(name, str):
            raise TypeError(
                "graph node names must be strings"
            )

        if not isinstance(definition, tuple):
            raise TypeError(
                f"definition for node '{name}' "
                "must be a tuple"
            )

        if len(definition) != 2:
            raise ValueError(
                f"definition for node '{name}' "
                "must contain dependencies and function"
            )

        dependencies, function = definition

        if not isinstance(dependencies, list):
            raise TypeError(
                f"dependencies for node '{name}' "
                "must be a list"
            )

        if not all(
            isinstance(dependency, str)
            for dependency in dependencies
        ):
            raise TypeError(
                f"dependencies for node '{name}' "
                "must contain strings"
            )

        if not callable(function):
            raise TypeError(
                f"function for node '{name}' "
                "must be callable"
            )

        for dependency in dependencies:

            if dependency not in graph:
                raise ValueError(
                    f"node '{name}' depends on missing node "
                    f"'{dependency}'"
                )


def _validate_acyclic(
    graph: GraphDefinition,
) -> None:
    """
    Validate that the graph contains no dependency cycles.

    Uses depth-first traversal with three states:

        0 = unvisited
        1 = currently visiting
        2 = completely visited

    A dependency pointing to a currently visiting node
    represents a cycle.
    """

    state: dict[str, int] = {
        node: 0
        for node in graph
    }

    def visit(node: str) -> None:

        if state[node] == 1:
            raise ValueError(
                "graph contains a cycle involving node "
                f"'{node}'"
            )

        if state[node] == 2:
            return

        state[node] = 1

        dependencies, _ = graph[node]

        for dependency in dependencies:
            visit(dependency)

        state[node] = 2

    for node in graph:
        visit(node)


# ---------------------------------------------------------------------------
# Task 2 — Dependency execution
# ---------------------------------------------------------------------------

def _find_ready_node(
    graph: GraphDefinition,
    completed: set[str],
) -> str | None:
    """
    Return the next node whose dependencies are complete.

    Dictionary insertion order provides deterministic behavior
    when multiple nodes are ready at the same time.
    """

    for name, (dependencies, _) in graph.items():

        if name in completed:
            continue

        if all(
            dependency in completed
            for dependency in dependencies
        ):
            return name

    return None


def run_graph(
    graph: GraphDefinition,
    inputs: dict,
    trace: list[str] | None = None,
) -> dict:
    """
    Execute the graph in dependency order.

    Each node receives only the outputs of its declared
    dependencies.

    Root nodes receive the initial input.

    Args:
        graph:
            Graph definition produced by build_graph().

        inputs:
            Input dictionary supplied to root nodes.

        trace:
            Optional list. Executed node names are appended
            in dependency order.

    Returns:
        Dictionary mapping every node name to its output.

    Raises:
        TypeError:
            For invalid graph/input/function/output types.

        ValueError:
            For missing dependencies or cycles.
    """

    # Validate graph structure first.
    _validate_graph(graph)

    # Validate cycles before executing any node.
    _validate_acyclic(graph)

    if not isinstance(inputs, dict):
        raise TypeError(
            "inputs must be a dictionary"
        )

    if trace is not None and not isinstance(trace, list):
        raise TypeError(
            "trace must be a list or None"
        )

    results: dict[str, dict] = {}
    completed: set[str] = set()

    while len(completed) < len(graph):

        node_name = _find_ready_node(
            graph,
            completed,
        )

        if node_name is None:

            unresolved = [
                name
                for name in graph
                if name not in completed
            ]

            raise ValueError(
                "graph cannot be executed because of a "
                "cycle or unresolved dependency: "
                + ", ".join(unresolved)
            )

        dependencies, function = graph[node_name]

        # Root nodes receive the original input.
        if not dependencies:

            node_input = dict(inputs)

        else:

            # Non-root nodes receive only the outputs
            # of their declared dependencies.
            node_input = {}

            for dependency in dependencies:

                dependency_output = results[dependency]

                if not isinstance(
                    dependency_output,
                    dict,
                ):
                    raise TypeError(
                        f"node '{dependency}' "
                        "must return a dictionary"
                    )

                node_input.update(
                    dependency_output
                )

        # Execute the node.
        result = function(node_input)

        if not isinstance(result, dict):
            raise TypeError(
                f"node '{node_name}' "
                "must return a dictionary"
            )

        # Store the node output.
        results[node_name] = result

        # Mark node as complete.
        completed.add(node_name)

        # Record execution order when tracing is requested.
        if trace is not None:
            trace.append(node_name)

    return results


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    """Run a deterministic demonstration of the graph."""

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

    print(
        "Topic 6 — Graph of Thought Execution"
    )
    print("=" * 50)

    print(
        f"execution order: {trace}"
    )

    print(
        f"merged result: {results['merge']}"
    )


if __name__ == "__main__":
    main()