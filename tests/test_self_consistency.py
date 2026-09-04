"""Self-consistency vote (eval_vllm.self_consistency_vote): gold-blind plurality over the
normalised literal, parse failures abstain, deterministic earliest-sample tie-break, and
the any-of-n ceiling is reported separately from the vote."""
from obtune.eval_vllm import self_consistency_vote
from obtune.schema import EvalItem

ITEM = EvalItem(
    item_id="p::L0::0", program_id="p", dataset="A", condition="L0", language="python",
    code="def f(x):\n    return x + 1\n", entry_point="f", args_repr="1", output_repr="2",
)


def _run(samples):
    return self_consistency_vote([[(t, 3) for t in samples]], [ITEM])


def test_plurality_wins_over_first_sample():
    outs, _, ex = _run(["3", "2", "2", "3", "2"])
    assert outs == ["2"]
    assert ex[0]["sc_agree"] == 3 / 5
    assert ex[0]["sc_any_correct"] == 1 and ex[0]["sc_first_correct"] == 0


def test_vote_key_is_normalised_literal_not_raw_text():
    # "2" and " 2 " are one answer, and so are 'abc' / "abc": vote on the parsed value.
    outs, _, ex = _run(["3", "2", " 2 "])
    assert outs[0].strip() == "2"
    assert ex[0]["sc_n_distinct"] == 2
    outs, _, ex = _run(["[1,2]", "[1, 2]", "'abc'", '"abc"', '"abc"'])
    assert outs == ["'abc'"] and ex[0]["sc_n_distinct"] == 2 and ex[0]["sc_agree"] == 3 / 5


def test_parse_failures_abstain_but_all_failed_returns_first():
    outs, _, ex = _run(["???", "!!", "2"])
    assert outs == ["2"] and ex[0]["sc_n_parsed"] == 1
    outs, _, ex = _run(["???", "!!"])
    assert outs == ["???"] and ex[0]["sc_n_parsed"] == 0 and ex[0]["sc_agree"] == 0.0


def test_tie_breaks_to_earliest_sample():
    outs, _, _ = _run(["3", "2", "2", "3"])
    assert outs == ["3"]


def test_any_correct_is_not_the_vote():
    outs, _, ex = _run(["3", "3", "3", "2"])
    assert outs == ["3"] and ex[0]["sc_any_correct"] == 1
