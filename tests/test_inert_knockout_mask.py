"""`inert_key_mask` must select the provably-dead tokens and nothing else.

The steering arm's whole claim is that the program is unchanged and only ATTENTION moves. If the
mask drifted onto live tokens the intervention would be suppressing material the answer depends
on, and a drop in accuracy would be read as "steering does not help" rather than "we masked the
computation". So the mask is pinned against the real tokenizer, not a synthetic offset list.
"""
import numpy as np
import pytest

from obtune.attention.knockout import KnockoutSpec, inert_key_mask

CODE = (
    "def solve(n):\n"
    "    off = 160\n"
    "    if (off * off + off) % 2 == 0:\n"
    "        scratch = 0\n"
    "        scratch += 2\n"
    "    total = 0\n"
    "    for i in range(n):\n"
    "        total += i\n"
    "    return total\n"
)


def _offsets(tok, prompt):
    enc = tok(prompt, return_offsets_mapping=True, add_special_tokens=False)
    return enc["offset_mapping"], enc["input_ids"]


@pytest.fixture(scope="module")
def tokenizer():
    from transformers import AutoTokenizer
    import yaml
    models = yaml.safe_load(open("configs/models.yaml"))
    entry = models["models"]["qwen25c-1.5b"] if "models" in models else models["qwen25c-1.5b"]
    name = entry["hf_id"] if isinstance(entry, dict) else entry
    return AutoTokenizer.from_pretrained(name)


def test_mask_covers_the_dead_block_and_spares_live_code(tokenizer):
    prefix = "Program:\n"
    prompt = prefix + CODE
    offsets, ids = _offsets(tokenizer, prompt)
    m = inert_key_mask(CODE, "python", "solve", offsets, len(prefix))
    assert m.any(), "nothing masked — the analysis or the offset mapping is wrong"

    masked_text = "".join(prompt[s:e] for (s, e), k in zip(offsets, m) if k)
    kept_text = "".join(prompt[s:e] for (s, e), k in zip(offsets, m) if not k)

    # the inert block is masked ...
    assert "scratch" in masked_text
    # ... and every token the answer depends on is not
    for live in ["return total", "for i in range(n)", "total += i", "def solve"]:
        assert live.split()[0] in kept_text
    assert "scratch" not in kept_text


def test_mask_is_empty_on_clean_code(tokenizer):
    clean = "def solve(n):\n    t = 0\n    for i in range(n):\n        t += i\n    return t\n"
    prompt = "Program:\n" + clean
    offsets, _ = _offsets(tokenizer, prompt)
    m = inert_key_mask(clean, "python", "solve", offsets, len("Program:\n"))
    assert not m.any(), "masked live code in a program with nothing dead in it"


def test_mask_never_leaves_the_code_region(tokenizer):
    prefix = "Instructions that must never be masked.\nProgram:\n"
    prompt = prefix + CODE
    offsets, _ = _offsets(tokenizer, prompt)
    m = inert_key_mask(CODE, "python", "solve", offsets, len(prefix))
    for (s, e), k in zip(offsets, m):
        if k:
            assert s >= len(prefix), f"masked token at {s} is inside the instructions"


def test_spec_accepts_inert_and_still_rejects_nonsense():
    KnockoutSpec(layers=(14,), classes=("inert",)).validate()
    KnockoutSpec(layers=(14,), classes=("inert", "identifier")).validate()
    with pytest.raises(ValueError):
        KnockoutSpec(layers=(14,), classes=("not_a_class",)).validate()
