"""Every panel model must build the SAME prompt text through the SAME builder.

CLAUDE.md §4 silent-failure #3. The panel grew on 2026-09-09 to models whose chat
templates refuse a system role (StarCoder2, CodeGemma) or have no template at all
(the pretrained Llama-3.1), so the adaptation in `prompts.py` is the thing standing
between that and a training/eval prompt divergence that no loss curve would show.

Tokenizers are read from HF_HOME; a model that is not on disk is skipped rather than
downloaded, so the suite still runs on a node with no network.
"""
from __future__ import annotations

import pytest

from obtune import prompts

# (models.yaml key or candidate key, hf id, expected mode). The expectation is the
# point of the test: a template that silently changes behaviour on an upgrade should
# fail here, not in a training run.
PANEL = [
    ("codellama-7b", "codellama/CodeLlama-7b-Instruct-hf", "system"),
    ("llama31-8b", "meta-llama/Llama-3.1-8B-Instruct", "system"),
    ("granite-3.1-8b-instruct", "ibm-granite/granite-3.1-8b-instruct", "system"),
    ("gemma3-12b-it", "google/gemma-3-12b-it", "system"),
    ("starcoder2-15b-instruct", "bigcode/starcoder2-15b-instruct-v0.1", "merged"),
    ("codegemma-7b-it", "google/codegemma-7b-it", "merged"),
    ("llama31-8b-base", "meta-llama/Llama-3.1-8B", "plain"),
]


def _tok(hf_id):
    transformers = pytest.importorskip("transformers")
    try:
        return transformers.AutoTokenizer.from_pretrained(hf_id, local_files_only=True)
    except Exception as exc:  # not on disk on this machine
        pytest.skip(f"{hf_id} not in HF_HOME ({type(exc).__name__})")


def _messages():
    return prompts.build_prompt(
        code="def f(x):\n    return x + 1\n",
        entry_point="f",
        args_repr="1",
        language="python",
        condition="L0",
    )


@pytest.mark.parametrize("key,hf_id,expected", PANEL, ids=[p[0] for p in PANEL])
def test_mode_is_what_we_declared(key, hf_id, expected):
    assert prompts.template_mode(_tok(hf_id)) == expected


@pytest.mark.parametrize("key,hf_id,expected", PANEL, ids=[p[0] for p in PANEL])
def test_system_text_survives_rendering(key, hf_id, expected):
    """The failure this whole layer exists to prevent: a template that quietly drops
    the system turn would train and evaluate on a prompt with no task description."""
    text = prompts.render_chat(_messages(), _tok(hf_id))
    head = prompts.SYSTEM_PROMPT.splitlines()[0]
    assert head in text
    assert "def f(x)" in text


@pytest.mark.parametrize("key,hf_id,expected", PANEL, ids=[p[0] for p in PANEL])
def test_prompt_is_a_prefix_of_prompt_plus_completion(key, hf_id, expected):
    """TRL's completion_only_loss contract (objectives.tokenize_pc asserts the token
    form of the same thing): if the prompt is not a prefix, the loss mask is wrong."""
    tok = _tok(hf_id)
    msgs = _messages()
    assert prompts.render_full(msgs, tok, completion="2").startswith(
        prompts.render_chat(msgs, tok).rstrip("\n") if expected == "plain"
        else prompts.render_chat(msgs, tok)
    )


@pytest.mark.parametrize("key,hf_id,expected", PANEL, ids=[p[0] for p in PANEL])
def test_trl_example_shape(key, hf_id, expected):
    tok = _tok(hf_id)
    ex = prompts.build_example(
        {"code": "def f(x):\n    return x + 1\n", "entry_point": "f", "args_repr": "1",
         "language": "python", "condition": "L0", "output_repr": "2"}
    )
    out = prompts.to_trl_example(ex, tok)
    if expected == "plain":
        assert isinstance(out["prompt"], str) and isinstance(out["completion"], str)
        assert out["prompt"] == prompts.render_chat(ex["prompt"], tok)
    else:
        assert isinstance(out["prompt"], list) and out["completion"][0]["role"] == "assistant"
        # what the trainer templates == what eval renders
        assert tok.apply_chat_template(
            out["prompt"], tokenize=False, add_generation_prompt=True
        ) == prompts.render_chat(ex["prompt"], tok)


def test_merged_preserves_content_without_a_tokenizer():
    msgs = [{"role": "system", "content": "SYS"}, {"role": "user", "content": "U"}]
    assert prompts.adapt_messages(msgs, None, force="merged") == [
        {"role": "user", "content": "SYS\n\nU"}
    ]


def test_merge_refuses_rather_than_dropping_the_system_turn():
    with pytest.raises(ValueError):
        prompts.adapt_messages([{"role": "system", "content": "SYS"}], None, force="merged")
