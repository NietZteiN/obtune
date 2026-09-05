"""Execution-trace arm (src/obtune/trace.py + prompts trace template).

Pure tests: no corpus, no model. The end-to-end loss-mask gate is scripts/inspect_batch.py
on configs/train/trace_generic_py_L0.yaml.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune import prompts, trace  # noqa: E402
from obtune.exec.pool import BatchItem, run_batch  # noqa: E402


def test_format_and_extract_roundtrip():
    c = trace.format_completion(["L2 x=1", "L3", "L4 x=2 y=[1,2]"], "[1,2]")
    assert c.endswith("\n=> [1,2]")
    assert trace.extract_answer(c) == "[1,2]"
    # The trace may itself contain "=>" inside a string value; only the LAST answer line counts.
    assert trace.extract_answer('L1 s="=> no"\n=> 7') == "7"
    # No answer line -> empty (grades as format_fail), never a guess from the trace.
    assert trace.extract_answer("L1 x=1\nL2 x=2") == ""
    assert trace.extract_answer("") == ""


def test_trace_template_is_separate_and_greedy_hash_is_stable():
    m_greedy = prompts.build_prompt("def f(x):\n    return x", "f", "(1)", "python")
    m_trace = prompts.build_prompt("def f(x):\n    return x", "f", "(1)", "python", trace=True)
    assert m_greedy[0]["content"] != m_trace[0]["content"]
    # The program/call block the model reads is byte-identical; only the last line differs.
    g, t = m_greedy[-1]["content"], m_trace[-1]["content"]
    assert g.rsplit("\n", 1)[0] == t.rsplit("\n", 1)[0]
    assert prompts.template_sha256() != prompts.template_sha256(trace=True)
    assert prompts.prompt_id(trace=True) == "trace_v1"
    assert prompts.provenance_block(trace=True)["prompt_id"] == "trace_v1"


def test_build_example_completion_override_switches_to_trace_prompt():
    row = {"code": "def f():\n    return 1", "entry_point": "f", "args_repr": "()",
           "language": "python", "output_repr": "1"}
    ex = prompts.build_example(row, completion="L2\n=> 1")
    assert ex["completion"][0]["content"] == "L2\n=> 1"
    assert ex["prompt"][0]["content"] == prompts.SYSTEM_PROMPT_TRACE
    assert prompts.build_example(row)["prompt"][0]["content"] == prompts.SYSTEM_PROMPT


def test_runner_trace_mode_records_changed_locals_and_answer():
    code = "def f(n):\n    s = 0\n    for i in range(n):\n        s += i\n    return s\n"
    item = BatchItem(program_id="t", language="python", code=code, entry_point="f",
                     args_reprs=["(3)"], trace={"max_events": 64, "max_repr": 48})
    res = run_batch([item], timeout_s=5.0, workers=1)[0].cases[0]
    assert res.status == "ok" and res.output == "3"
    assert res.trace is not None and res.trace[0].startswith("L2")
    assert any("s=3" in e for e in res.trace)
    assert "..." not in res.trace  # well inside the budget


def test_runner_trace_budget_cuts_with_single_marker():
    code = "def f(n):\n    s = 0\n    for i in range(n):\n        s += i\n    return s\n"
    item = BatchItem(program_id="t", language="python", code=code, entry_point="f",
                     args_reprs=["(100)"], trace={"max_events": 8, "max_repr": 48})
    res = run_batch([item], timeout_s=5.0, workers=1)[0].cases[0]
    assert res.status == "ok" and res.output == "4950"  # tracing stops; execution does not
    assert res.trace[-1] == "..." and res.trace.count("...") == 1 and len(res.trace) == 9
