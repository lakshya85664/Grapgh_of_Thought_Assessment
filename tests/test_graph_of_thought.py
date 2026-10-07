import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from graph_of_thought import build_graph, run_graph


def test_graph_contains_at_least_six_nodes():
    graph = build_graph()

    assert len(graph) >= 6


def test_graph_contains_required_nodes():
    graph = build_graph()

    required_nodes = {
        "read",
        "normalize",
        "split",
        "keywords",
        "counts",
        "merge",
    }

    assert required_nodes.issubset(graph.keys())


def test_each_node_has_dependencies_and_callable():
    graph = build_graph()

    for name, definition in graph.items():
        dependencies, function = definition

        assert isinstance(name, str)
        assert isinstance(dependencies, list)
        assert callable(function)


def test_normalization_depends_on_read():
    graph = build_graph()

    dependencies, _ = graph["normalize"]

    assert dependencies == ["read"]


def test_split_depends_on_normalize():
    graph = build_graph()

    dependencies, _ = graph["split"]

    assert dependencies == ["normalize"]


def test_two_branches_depend_on_split():
    graph = build_graph()

    keyword_dependencies, _ = graph["keywords"]
    count_dependencies, _ = graph["counts"]

    assert keyword_dependencies == ["split"]
    assert count_dependencies == ["split"]


def test_merge_depends_on_both_branches():
    graph = build_graph()

    dependencies, _ = graph["merge"]

    assert set(dependencies) == {
        "keywords",
        "counts",
    }


def test_graph_has_two_branch_merge_structure():
    graph = build_graph()

    keyword_dependencies, _ = graph["keywords"]
    count_dependencies, _ = graph["counts"]
    merge_dependencies, _ = graph["merge"]

    assert keyword_dependencies == ["split"]
    assert count_dependencies == ["split"]

    assert set(merge_dependencies) == {
        "keywords",
        "counts",
    }


def test_all_graph_functions_are_callable():
    graph = build_graph()

    for _, (_, function) in graph.items():
        assert callable(function)


def test_run_graph_executes_in_dependency_order():
    graph = build_graph()
    trace = []

    run_graph(
        graph,
        {
            "text": (
                "Agents plan tasks. "
                "Agents execute tasks."
            )
        },
        trace,
    )

    assert trace == [
        "read",
        "normalize",
        "split",
        "keywords",
        "counts",
        "merge",
    ]


def test_run_graph_returns_all_node_outputs():
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

    assert set(results) == {
        "read",
        "normalize",
        "split",
        "keywords",
        "counts",
        "merge",
    }


def test_run_graph_produces_expected_merge_result():
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

    assert results["merge"]["sentences"] == 2
    assert results["merge"]["keywords"] == [
        "agents",
        "plan",
        "tasks",
        "agents",
        "execute",
    ]


def test_trace_is_optional():
    graph = build_graph()

    results = run_graph(
        graph,
        {
            "text": "One sentence.",
        },
    )

    assert "merge" in results


def test_root_node_receives_initial_input():
    graph = build_graph()
    trace = []

    results = run_graph(
        graph,
        {
            "text": "Hello world.",
        },
        trace,
    )

    assert results["read"]["text"] == "Hello world."


def test_dependency_outputs_are_available_to_downstream_nodes():
    graph = build_graph()

    results = run_graph(
        graph,
        {
            "text": "First sentence. Second sentence.",
        },
    )

    assert results["normalize"]["text"] == (
        "First sentence. Second sentence."
    )

    assert results["split"]["sentences"] == [
        "First sentence",
        "Second sentence",
    ]


def test_missing_dependency_is_rejected():
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
        assert "missing node" in str(error)
    else:
        raise AssertionError(
            "Expected missing dependency to raise ValueError"
        )

def test_merge_combines_two_branch_outputs():
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

    merged = results["merge"]

    assert merged == {
        "keywords": [
            "agents",
            "plan",
            "tasks",
            "agents",
            "execute",
        ],
        "sentences": 2,
    }


def test_merge_requires_keywords_branch():
    graph = build_graph()

    _, merge_function = graph["merge"]

    try:
        merge_function(
            {
                "counts": 2,
            }
        )
    except ValueError as error:
        assert "keywords" in str(error)
    else:
        raise AssertionError(
            "Expected missing keywords output to raise ValueError"
        )


def test_merge_requires_counts_branch():
    graph = build_graph()

    _, merge_function = graph["merge"]

    try:
        merge_function(
            {
                "keywords": ["agents"],
            }
        )
    except ValueError as error:
        assert "counts" in str(error)
    else:
        raise AssertionError(
            "Expected missing counts output to raise ValueError"
        )


def test_merge_rejects_invalid_keywords_type():
    graph = build_graph()

    _, merge_function = graph["merge"]

    try:
        merge_function(
            {
                "keywords": "agents",
                "counts": 2,
            }
        )
    except TypeError as error:
        assert "keywords" in str(error)
    else:
        raise AssertionError(
            "Expected invalid keywords type to raise TypeError"
        )


def test_merge_rejects_invalid_counts_type():
    graph = build_graph()

    _, merge_function = graph["merge"]

    try:
        merge_function(
            {
                "keywords": ["agents"],
                "counts": "2",
            }
        )
    except TypeError as error:
        assert "counts" in str(error)
    else:
        raise AssertionError(
            "Expected invalid counts type to raise TypeError"
        )


def test_merge_does_not_modify_keyword_input():
    graph = build_graph()

    _, merge_function = graph["merge"]

    keywords = [
        "agents",
        "plan",
    ]

    result = merge_function(
        {
            "keywords": keywords,
            "counts": 1,
        }
    )

    result["keywords"].append("extra")

    assert keywords == [
        "agents",
        "plan",
    ]


def test_merge_preserves_branch_outputs():
    graph = build_graph()

    results = run_graph(
        graph,
        {
            "text": "Planning improves execution.",
        },
    )

    keywords = results["keywords"]["keywords"]
    counts = results["counts"]["counts"]
    merged = results["merge"]

    assert merged["keywords"] == keywords
    assert merged["sentences"] == counts

def test_missing_dependency_is_rejected_before_execution():
    graph = build_graph()

    graph["merge"] = (
        ["does_not_exist"],
        lambda data: data,
    )

    trace = []

    try:
        run_graph(
            graph,
            {
                "text": "Example.",
            },
            trace,
        )
    except ValueError as error:
        assert "missing node" in str(error)
    else:
        raise AssertionError(
            "Expected missing dependency to raise ValueError"
        )


def test_two_node_cycle_is_rejected():
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
        assert "cycle" in str(error).lower()
    else:
        raise AssertionError(
            "Expected two-node cycle to raise ValueError"
        )


def test_three_node_cycle_is_rejected():
    graph = {
        "a": (
            ["c"],
            lambda data: data,
        ),
        "b": (
            ["a"],
            lambda data: data,
        ),
        "c": (
            ["b"],
            lambda data: data,
        ),
    }

    try:
        run_graph(
            graph,
            {},
        )
    except ValueError as error:
        assert "cycle" in str(error).lower()
    else:
        raise AssertionError(
            "Expected three-node cycle to raise ValueError"
        )


def test_self_dependency_is_rejected():
    graph = {
        "a": (
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
        assert "cycle" in str(error).lower()
    else:
        raise AssertionError(
            "Expected self-cycle to raise ValueError"
        )


def test_valid_graph_is_not_rejected_as_cyclic():
    graph = build_graph()

    results = run_graph(
        graph,
        {
            "text": "Valid graph.",
        },
    )

    assert "merge" in results


def test_cycle_detection_prevents_partial_execution():
    execution = []

    def node_a(data):
        execution.append("a")
        return data

    def node_b(data):
        execution.append("b")
        return data

    graph = {
        "a": (
            ["b"],
            node_a,
        ),
        "b": (
            ["a"],
            node_b,
        ),
    }

    try:
        run_graph(
            graph,
            {},
        )
    except ValueError as error:
        assert "cycle" in str(error).lower()
    else:
        raise AssertionError(
            "Expected cycle to raise ValueError"
        )

    assert execution == []

def test_paragraph_analysis_returns_structured_result():
    from thought_graph.cli import analyze_paragraph

    result = analyze_paragraph(
        "Agents plan tasks. Agents execute tasks."
    )

    assert "input" in result
    assert "analysis" in result
    assert "execution" in result


def test_paragraph_analysis_counts_sentences():
    from thought_graph.cli import analyze_paragraph

    result = analyze_paragraph(
        "First sentence. Second sentence."
    )

    assert result["analysis"]["sentence_count"] == 2


def test_paragraph_analysis_returns_sentences():
    from thought_graph.cli import analyze_paragraph

    result = analyze_paragraph(
        "First sentence. Second sentence."
    )

    assert result["analysis"]["sentences"] == [
        "First sentence",
        "Second sentence",
    ]


def test_paragraph_analysis_returns_keywords():
    from thought_graph.cli import analyze_paragraph

    result = analyze_paragraph(
        "Agents plan tasks. Agents execute tasks."
    )

    assert result["analysis"]["keywords"] == [
        "agents",
        "plan",
        "tasks",
        "agents",
        "execute",
    ]


def test_paragraph_analysis_records_graph_execution():
    from thought_graph.cli import analyze_paragraph

    result = analyze_paragraph(
        "Agents plan tasks."
    )

    assert result["execution"]["order"] == [
        "read",
        "normalize",
        "split",
        "keywords",
        "counts",
        "merge",
    ]

    assert result["execution"]["node_count"] == 6


def test_paragraph_analysis_contains_merged_output():
    from thought_graph.cli import analyze_paragraph

    result = analyze_paragraph(
        "Agents plan tasks."
    )

    assert result["analysis"]["merged"] == {
        "keywords": [
            "agents",
            "plan",
            "tasks",
        ],
        "sentences": 1,
    }


def test_empty_paragraph_is_rejected():
    from thought_graph.cli import analyze_paragraph

    try:
        analyze_paragraph("   ")
    except ValueError as error:
        assert "empty" in str(error)
    else:
        raise AssertionError(
            "Expected empty paragraph to raise ValueError"
        )


def test_non_string_paragraph_is_rejected():
    from thought_graph.cli import analyze_paragraph

    try:
        analyze_paragraph(123)
    except TypeError as error:
        assert "string" in str(error)
    else:
        raise AssertionError(
            "Expected non-string paragraph to raise TypeError"
        )

def test_cli_rejects_missing_input_file(tmp_path):
    from thought_graph.cli import _load_input

    missing_file = tmp_path / "missing.json"

    try:
        _load_input(missing_file)
    except FileNotFoundError as error:
        assert "does not exist" in str(error)
    else:
        raise AssertionError(
            "Expected missing input file to raise FileNotFoundError"
        )


def test_cli_rejects_invalid_json(tmp_path):
    from thought_graph.cli import _load_input

    invalid_file = tmp_path / "invalid.json"

    invalid_file.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    try:
        _load_input(invalid_file)
    except ValueError as error:
        assert "invalid JSON" in str(error)
    else:
        raise AssertionError(
            "Expected invalid JSON to raise ValueError"
        )


def test_cli_rejects_missing_text_field(tmp_path):
    from thought_graph.cli import _load_input

    input_file = tmp_path / "missing_text.json"

    input_file.write_text(
        '{"message": "hello"}',
        encoding="utf-8",
    )

    try:
        _load_input(input_file)
    except ValueError as error:
        assert "'text'" in str(error)
    else:
        raise AssertionError(
            "Expected missing text field to raise ValueError"
        )


def test_cli_rejects_non_string_text(tmp_path):
    from thought_graph.cli import _load_input

    input_file = tmp_path / "wrong_type.json"

    input_file.write_text(
        '{"text": 123}',
        encoding="utf-8",
    )

    try:
        _load_input(input_file)
    except TypeError as error:
        assert "string" in str(error)
    else:
        raise AssertionError(
            "Expected non-string text to raise TypeError"
        )


def test_analysis_is_deterministic():
    from thought_graph.cli import analyze_paragraph

    text = (
        "Agents plan tasks. "
        "Agents execute tasks."
    )

    first = analyze_paragraph(text)
    second = analyze_paragraph(text)

    assert first == second


def test_analysis_handles_single_sentence():
    from thought_graph.cli import analyze_paragraph

    result = analyze_paragraph(
        "A single sentence."
    )

    assert result["analysis"]["sentence_count"] == 1

    assert result["analysis"]["sentences"] == [
        "A single sentence"
    ]


def test_analysis_handles_extra_whitespace():
    from thought_graph.cli import analyze_paragraph

    result = analyze_paragraph(
        "   First sentence. Second sentence.   "
    )

    assert result["analysis"]["normalized_text"] == (
        "First sentence. Second sentence."
    )

    assert result["analysis"]["sentence_count"] == 2