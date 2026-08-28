"""`train.shuffle_labels` must destroy the input->answer mapping and NOTHING else.

The format-only arm (configs/train/formatonly_qwen1.5b_py.yaml) is only interpretable if the
shuffle is a pure permutation: same rows, same programs, same multiset of answers, same count.
If it dropped rows or altered the answer distribution, the arm would confound "cannot learn the
task" with "saw less/different data", which is exactly what it exists to rule out.
"""
import json

from obtune.data import build_sft_splits


def _text(rec):
    """`prompt`/`completion` are chat-message lists; compare them as canonical JSON."""
    return json.dumps(rec, sort_keys=True)


def _cfg(**over):
    cfg = {"language": "python", "train_conditions": ["L0"],
           "train": {"seed": 17, "train_size": 200, "val_size": 40}}
    cfg["train"].update(over)
    return cfg


def test_shuffle_labels_permutes_answers_without_changing_the_data():
    honest = build_sft_splits(_cfg())
    shuffled = build_sft_splits(_cfg(shuffle_labels=True))

    h_tr, s_tr = honest["train"], shuffled["train"]
    assert len(h_tr) == len(s_tr), "shuffle must not change the row count"

    h_completions = sorted(_text(r["completion"]) for r in h_tr)
    s_completions = sorted(_text(r["completion"]) for r in s_tr)
    assert h_completions == s_completions, "shuffle must be a permutation of the same answers"

    h_prompts = [_text(r["prompt"]) for r in h_tr]
    s_prompts = [_text(r["prompt"]) for r in s_tr]
    assert h_prompts == s_prompts, "shuffle must leave prompts (and their order) untouched"

    # and it must actually break the mapping for most rows
    moved = sum(1 for a, b in zip(h_tr, s_tr) if _text(a["completion"]) != _text(b["completion"]))
    assert moved > 0.5 * len(h_tr), f"only {moved}/{len(h_tr)} labels moved — shuffle is a no-op"


def test_shuffle_labels_leaves_val_honest():
    """Checkpoint selection must still measure genuine accuracy (documented asymmetry)."""
    honest = build_sft_splits(_cfg())
    shuffled = build_sft_splits(_cfg(shuffle_labels=True))
    assert [_text(r["completion"]) for r in honest["val"]] == [_text(r["completion"]) for r in shuffled["val"]]


def test_shuffle_labels_defaults_off():
    a = build_sft_splits(_cfg())
    b = build_sft_splits(_cfg(shuffle_labels=False))
    assert [_text(r["completion"]) for r in a["train"]] == [_text(r["completion"]) for r in b["train"]]
