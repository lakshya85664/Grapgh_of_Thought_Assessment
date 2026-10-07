# Topic 6: Create an Executable Graph of Thought Workflow

## Project Overview
This project implements an executable Graph of Thought workflow in Python using a directed acyclic graph (DAG). The workflow contains six nodes, two branches, a merge node, dependency-aware execution, graph validation, cycle detection, missing-dependency handling, and a paragraph-analysis application.

The implementation is deterministic, local, reproducible, and does not require external APIs, network access, or credentials.

## Graph Architecture

```text
read
  |
  v
normalize
  |
  v
split
  |
  +------> keywords
  |
  +------> counts
             |
             v
           merge
```

Nodes:
1. `read`
2. `normalize`
3. `split`
4. `keywords`
5. `counts`
6. `merge`

The `split` node creates two independent branches. The `keywords` and `counts` branches are combined by `merge`.

## Assessment Tasks

### Task 1 — Define the Graph
`build_graph()` defines a six-node graph with explicit dependencies, two branches, and a final merge node.

### Task 2 — Dependency-Aware Execution
`run_graph()` validates the graph and executes nodes only after their dependencies complete. It tracks completed nodes and supports an execution trace.

Verified execution order:
```text
read → normalize → split → keywords → counts → merge
```

### Task 3 — Merge Strategy
The `merge` node combines:
- `keywords` → deterministic keyword list
- `counts` → sentence count

Verified merged result:
```json
{
  "keywords": ["agents", "plan", "tasks", "agents", "execute"],
  "sentences": 2
}
```

### Task 4 — Cycles and Missing Dependencies
The executor safely rejects invalid graphs, including:
- missing dependencies
- two-node cycles
- three-node cycles
- self-cycles
- invalid graph structures
- invalid node outputs

Invalid graphs are rejected before partial execution.

### Task 5 — Paragraph Analysis
Input:
```json
{
  "text": "Agents plan tasks. Agents execute tasks."
}
```

CLI:
```cmd
python -m thought_graph.cli analyze --input examples\paragraph.json --output outputs\analysis.json
```

Verified output:
```text
Execution order: ['read', 'normalize', 'split', 'keywords', 'counts', 'merge']
Sentence count: 2
Keywords: ['agents', 'plan', 'tasks', 'agents', 'execute']
```

## Project Structure

```text
Graph_of_Thought_Assessment/
├── src/
│   └── graph_of_thought.py
├── thought_graph/
│   ├── __init__.py
│   └── cli.py
├── tests/
│   └── test_graph_of_thought.py
├── evidence/
│   ├── traces/
│   │   ├── cycle_rejection.json
│   │   ├── execution_trace.json
│   │   ├── missing_dependency_rejection.json
│   │   ├── paragraph_analysis.json
│   │   └── test_summary.json
│   ├── state_snapshots/
│   │   ├── branch_outputs.json
│   │   └── graph_structure.json
│   └── generate_evidence.py
├── examples/
│   └── paragraph.json
├── outputs/
│   └── analysis.json
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

```cmd
cd /d E:\Tayana_Projects\Agent_Planning_and_Reasoning\Graph_of_Thought_Assessment
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Testing

Run:
```cmd
python -m pytest -q
```

Final verified result:
```text
44 passed in 0.10s
```

Coverage includes graph structure, dependency execution, branches, merge behavior, cycle detection, missing dependencies, invalid inputs, deterministic output, and paragraph-analysis boundary cases.

## Evidence Generation

Run:
```cmd
python evidence\generate_evidence.py
```

Expected:
```text
Topic 6 evidence generated successfully.
```

Evidence artifacts:
- `execution_trace.json`
- `paragraph_analysis.json`
- `cycle_rejection.json`
- `missing_dependency_rejection.json`
- `test_summary.json`
- `graph_structure.json`
- `branch_outputs.json`

## Design and Safety

The implementation uses deterministic local execution, explicit dependencies, validation before execution, typed input/output checks, structured JSON evidence, reproducible tests, and no external API or credential requirements.

## Reflection

This activity helped me understand how a reasoning workflow can be represented as an executable graph instead of a single linear chain. The most useful part was separating the graph definition from the execution engine. Each node declares its dependencies, while `run_graph()` determines when that node is ready to execute. This makes the workflow easier to reason about, test, and extend.

The branching structure clarified how Graph of Thought can support tasks with multiple independent reasoning paths. In this project, `split` creates two branches: keyword extraction and sentence counting. These branches can be developed independently and are later combined by `merge`. The same design can be extended to more complex analysis pipelines.

Another important learning point was graph validation. A workflow should not begin execution if its dependency structure is invalid. I therefore added checks for missing dependencies and cycles, including self-cycles and multi-node cycles. This prevents ambiguous or partially executed workflows.

The paragraph-analysis example connected the abstract graph structure to a practical use case. The execution trace and evidence files also made the workflow easier to inspect and verify.

Overall, this project strengthened my understanding of dependency-based execution, branching and merging, deterministic workflows, validation, and test-driven implementation. It provides a foundation that could later be extended with parallel execution, richer state tracking, or production-oriented scheduling.
