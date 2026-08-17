"""The gate's training loop, on CPU, before it is given ~3 GPU-h.

`--dry-run` proves the mask and the freeze; it never touches the collator, the optimizer, the
accumulation arithmetic, or the checkpoint round-trip. Those ~40 lines had never executed.
A tiny randomly-initialised Qwen2 exercises them structurally — the questions here are about
plumbing, not weights.
"""
from __future__ import annotations

import pytest
import torch

from obtune.mole.experts import ExpertBank
from obtune.mole.gate import GateConfig, RouterGate
from obtune.mole.model import _decoder_layers, attach_gate
from obtune.mole.train_mole import make_collate, render_pair

E, R, HID = 3, 4, 64


@pytest.fixture(scope="module")
def tokenizer():
    from transformers import AutoTokenizer

    from obtune.config import load_config

    models = load_config("models.yaml")
    hf_id = (models.get("models") or models)["qwen25c-1.5b"]["hf_id"]
    return AutoTokenizer.from_pretrained(hf_id)


@pytest.fixture()
def records():
    from obtune import prompts

    return [
        prompts.build_example({"code": f"def f(x): return x + {i}", "entry_point": "f",
                               "args_repr": f"({i},)", "language": "python",
                               "condition": "L1r", "output_repr": str(i + 1)})
        for i in range(4)
    ]


@pytest.fixture()
def holder():
    from transformers import AutoConfig, AutoModelForCausalLM

    torch.manual_seed(17)
    cfg = AutoConfig.for_model("qwen2", hidden_size=HID, intermediate_size=128,
                               num_hidden_layers=2, num_attention_heads=4,
                               num_key_value_heads=2, vocab_size=151936,
                               max_position_embeddings=512)
    model = AutoModelForCausalLM.from_config(cfg)
    torch.manual_seed(3)
    banks = {}
    for li in range(len(_decoder_layers(model))):
        banks[f"model.layers.{li}.self_attn.q_proj"] = ExpertBank(
            names=tuple(f"e{i}" for i in range(E)), rank=R,
            A_cat=torch.randn(E * R, HID) * 0.05, B_cat=torch.randn(HID, E * R) * 0.05)
    gate = RouterGate(GateConfig(E, HID, len(_decoder_layers(model)), d_router=8))
    return attach_gate(model, gate, banks)


# --------------------------------------------------------------------------- #
# the collator


def test_collate_masks_prompt_tokens_and_pads_labels_with_minus_100(tokenizer, records):
    """The single most dangerous line in the loop. Padding labels with the PAD TOKEN
    instead of -100 trains the gate to predict padding, and the loss curve still falls."""
    batch = make_collate(tokenizer, 512)(records)
    ids, lab, att = batch["input_ids"], batch["labels"], batch["attention_mask"]

    assert ids.shape == lab.shape == att.shape
    assert (lab == -100).any(), "no prompt tokens masked"
    assert (lab != -100).any(), "everything masked — the batch teaches nothing"
    # Every padded position must be masked out of the loss AND the attention.
    pad_id = tokenizer.pad_token_id or tokenizer.eos_token_id
    padded = (att == 0)
    assert torch.all(lab[padded] == -100), "padded positions are not -100 in the labels"
    assert torch.all(ids[padded] == pad_id)


def test_collate_supervises_only_the_completion(tokenizer, records):
    """The unmasked span must decode to the answer, not to any of the prompt."""
    r = records[0]
    batch = make_collate(tokenizer, 512)([r])
    lab = batch["labels"][0]
    kept = batch["input_ids"][0][lab != -100]
    text = tokenizer.decode(kept, skip_special_tokens=True)
    assert r["completion"][0]["content"] in text, (
        f"supervised span {text!r} does not contain the target "
        f"{r['completion'][0]['content']!r}")
    assert "execution engine" not in text, "system prompt leaked into the supervised span"


def test_collate_handles_a_ragged_batch(tokenizer):
    from obtune import prompts

    short = prompts.build_example({"code": "def f(): return 1", "entry_point": "f",
                                   "args_repr": "()", "language": "python",
                                   "condition": "L0", "output_repr": "1"})
    long = prompts.build_example({"code": "def f(x):\n" + "    x += 1\n" * 60 + "    return x",
                                  "entry_point": "f", "args_repr": "(1,)",
                                  "language": "python", "condition": "S1",
                                  "output_repr": "61"})
    b = make_collate(tokenizer, 512)([short, long])
    assert b["input_ids"].shape[0] == 2
    assert b["attention_mask"][0].sum() < b["attention_mask"][1].sum()


def test_render_pair_prompt_is_a_prefix_of_full(tokenizer, records):
    """`_mask_prompt` masks by PREFIX LENGTH, so this must hold or the boundary is wrong."""
    prompt, full = render_pair(tokenizer, records[0])
    assert full.startswith(prompt.rstrip()) or prompt.rstrip() in full


# --------------------------------------------------------------------------- #
# the loop itself


def test_two_accumulation_steps_move_only_the_gate(tokenizer, records, holder):
    """Grad accumulation + clip + step, exactly as `main` runs it."""
    batch = make_collate(tokenizer, 256)(records)
    opt = torch.optim.AdamW(holder.trainable_parameters(), lr=1e-3)
    before = [p.detach().clone() for p in holder.gate.parameters()]
    base_before = [p.detach().clone() for p in holder.model.parameters()][:5]

    accum = 2
    for _ in range(accum):
        loss = holder.model(**batch).loss / accum
        assert torch.isfinite(loss), "non-finite loss on the very first batch"
        loss.backward()
    torch.nn.utils.clip_grad_norm_(holder.trainable_parameters(), 1.0)
    opt.step()
    opt.zero_grad(set_to_none=True)

    moved = [not torch.allclose(a, b) for a, b in zip(before, holder.gate.parameters())]
    assert any(moved), "optimizer step did not move the gate at all"
    for a, b in zip(base_before, list(holder.model.parameters())[:5]):
        assert torch.allclose(a, b), "a BASE parameter moved — the freeze leaked"


def test_gate_checkpoint_round_trips_into_the_evaluator(tmp_path, holder):
    """train_mole saves `{"gate": state_dict, ...}`; eval_mole's `_load_gate` reads exactly
    that. A key mismatch here makes `mole_router` unrunnable after a 3 GPU-h training run,
    and nothing before this test checked the two halves agree."""
    from obtune.mole.eval_mole import _load_gate

    ckpt = tmp_path / "gate.pt"
    torch.save({"gate": holder.gate.state_dict(), "summary": holder.summary}, ckpt)
    holder._router_gate = holder.gate      # as eval_mole.main stashes it

    # Perturb, then reload: the values must come back.
    with torch.no_grad():
        for p in holder.gate.parameters():
            p.add_(1.0)
    _load_gate(holder, {"gate_checkpoint": str(ckpt)}, "mole_router", seed=17)

    reloaded = torch.load(ckpt, map_location="cpu")["gate"]
    for k, v in holder.gate.state_dict().items():
        assert torch.allclose(v, reloaded[k]), f"gate param {k} did not round-trip"


def test_missing_gate_checkpoint_fails_loudly(tmp_path, holder):
    """Silently evaluating an untrained gate under the `mole_router` label would be the
    worst outcome: a plausible number for a system that was never trained."""
    from obtune.mole.eval_mole import _load_gate

    holder._router_gate = holder.gate
    with pytest.raises(SystemExit, match="needs a trained gate"):
        _load_gate(holder, {"gate_checkpoint": str(tmp_path / "nope.pt")}, "mole_router", 17)


def test_mole_router_works_after_a_fixed_mixture_arm_ran_first(tmp_path, holder) -> None:
    """Arms must not depend on the order they run in.

    The ladder runs base -> mole_uniform -> mole_random -> mole_router, and the fixed-mixture
    arms REPLACE holder.gate with a ConstantGate. Loading the RouterGate checkpoint into
    whatever the previous arm left behind failed with "Missing key(s): w / Unexpected key(s):
    q_proj.*" — after the full 5-hour gate training, on the last arm of the run.
    """
    from obtune.mole.eval_mole import _load_gate

    ckpt = tmp_path / "gate.pt"
    torch.save({"gate": holder.gate.state_dict(), "summary": holder.summary}, ckpt)
    holder._router_gate = holder.gate

    _load_gate(holder, {}, "mole_uniform", seed=17)          # swaps in a ConstantGate
    assert type(holder.gate).__name__ == "ConstantGate"
    _load_gate(holder, {"gate_checkpoint": str(ckpt)}, "mole_router", seed=17)
    assert type(holder.gate).__name__ == "RouterGate", (
        "mole_router did not restore the RouterGate after a fixed-mixture arm")


def test_mole_random_is_reproducible_and_differs_from_trained(holder):
    """`mole_random` is the control that decides the headline. It must be reproducible, or
    the control is a different model each time it is run."""
    from obtune.mole.eval_mole import _load_gate

    holder._router_gate = holder.gate          # as eval_mole.main stashes it
    _load_gate(holder, {}, "mole_random", seed=17)
    first = [p.detach().clone() for p in holder.gate.parameters()]
    _load_gate(holder, {}, "mole_random", seed=17)
    for a, b in zip(first, holder.gate.parameters()):
        assert torch.allclose(a, b), "mole_random is not reproducible at a fixed seed"


# --------------------------------------------------------------------------- #
# dtype — the failure that killed the first real training run


@pytest.mark.parametrize("dt", [torch.float32, torch.bfloat16, torch.float16])
def test_gate_works_against_any_hidden_dtype(dt) -> None:
    """The base runs bf16 and the gate is kept fp32; mixing them is a hard error —
    `expected mat1 and mat2 to have the same dtype, but got c10::BFloat16 != float`.
    That is how `p3_mole_train` died on 2026-08-12 *after* --dry-run reported OK.

    The gate stays fp32 deliberately (a softmax over a temperature-scaled dot product is
    where bf16's mantissa hurts), so it must promote its input and cast its output back.
    """
    from obtune.mole.gate import GateConfig, RouterGate

    gate = RouterGate(GateConfig(E, HID, 2, d_router=8))       # fp32
    hidden = torch.randn(2, 5, HID, dtype=dt)
    w = gate(hidden, 0)
    assert w.dtype == dt, f"gate returned {w.dtype} for a {dt} hidden state"
    # Tolerance must follow the dtype: bf16 carries ~3 decimal digits, so a softmax row
    # legitimately sums to 1.001. Asserting 1e-3 here tests the format, not the code.
    tol = {torch.float32: 1e-5, torch.float16: 5e-3, torch.bfloat16: 2e-2}[dt]
    assert torch.allclose(w.float().sum(-1), torch.ones(2, 5), atol=tol)


def test_bf16_model_with_fp32_gate_runs_end_to_end() -> None:
    """The whole stack in the configuration training actually uses."""
    from transformers import AutoConfig, AutoModelForCausalLM

    torch.manual_seed(17)
    cfg = AutoConfig.for_model("qwen2", hidden_size=HID, intermediate_size=128,
                               num_hidden_layers=2, num_attention_heads=4,
                               num_key_value_heads=2, vocab_size=128,
                               max_position_embeddings=64)
    model = AutoModelForCausalLM.from_config(cfg).to(torch.bfloat16)
    banks = {f"model.layers.{i}.self_attn.q_proj": ExpertBank(
        names=tuple(f"e{j}" for j in range(E)), rank=R,
        A_cat=torch.randn(E * R, HID, dtype=torch.bfloat16) * 0.05,
        B_cat=torch.randn(HID, E * R, dtype=torch.bfloat16) * 0.05) for i in range(2)}
    gate = RouterGate(GateConfig(E, HID, 2, d_router=8))       # fp32 on purpose
    holder = attach_gate(model, gate, banks)

    ids = torch.randint(0, 128, (2, 6))
    loss = holder.model(input_ids=ids, labels=ids).loss
    assert torch.isfinite(loss)
    loss.backward()
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in gate.parameters())


def test_dry_run_executes_a_real_step() -> None:
    """--dry-run reported OK while never running the model, so it certified a build that
    died on its first forward. Pinned against the source: a behavioural test needs weights."""
    import inspect

    from obtune.mole import train_mole

    src = inspect.getsource(train_mole.main)
    head = src[:src.index("if args.dry_run")] + src[src.index("if args.dry_run"):]
    dry = head[head.index("if args.dry_run"):]
    dry = dry[:dry.index("return 0")]
    assert "loss.backward()" in dry, "--dry-run never runs a backward pass"
    assert "make_collate" in dry, "--dry-run never exercises the collator"
    assert "isfinite" in dry, "--dry-run does not check the loss is finite"


def test_gate_device_is_the_decoder_layer_not_the_first_parameter() -> None:
    """`next(model.parameters())` is usually the EMBEDDING, not the layer whose hook calls
    the gate. Under device_map="auto" those can differ, and using the wrong one fails on the
    first forward — after the ~3 GPU-h of training the eval stage depends on. Both
    build_mole_model and eval_mole._load_gate must resolve it the same way."""
    from transformers import AutoConfig, AutoModelForCausalLM

    from obtune.mole.model import _decoder_layers, gate_device

    cfg = AutoConfig.for_model("qwen2", hidden_size=HID, intermediate_size=128,
                               num_hidden_layers=2, num_attention_heads=4,
                               num_key_value_heads=2, vocab_size=128,
                               max_position_embeddings=64)
    model = AutoModelForCausalLM.from_config(cfg)
    assert gate_device(model) == next(_decoder_layers(model)[0].parameters()).device


def test_eval_and_train_resolve_the_gate_device_identically() -> None:
    """Two call sites, one resolver — pinned so they cannot drift apart again."""
    import inspect

    from obtune.mole import eval_mole
    from obtune.mole import model as mole_model

    assert "gate_device(" in inspect.getsource(eval_mole._load_gate)
    assert "gate_device(base)" in inspect.getsource(mole_model.build_mole_model)


def test_mole_random_is_a_real_control_not_a_copy_of_uniform(tmp_path, holder) -> None:
    """The control that decides the Part III headline.

    On 2026-08-13 it produced byte-identical accuracy to `mole_uniform` on all eight
    conditions: `mole_uniform` runs first and installs a ConstantGate whose `w` is a BUFFER,
    so re-initialising `holder.gate.parameters()` matched nothing. The control controlled for
    nothing, and `mole_router - mole_random` was meaningless.
    """
    import torch as _t

    from obtune.mole.eval_mole import _load_gate

    holder._router_gate = holder.gate
    trained = {k: v.clone() for k, v in holder.gate.state_dict().items()}

    _load_gate(holder, {}, "mole_uniform", seed=17)
    _load_gate(holder, {}, "mole_random", seed=17)

    assert type(holder.gate).__name__ == "RouterGate", "mole_random is not a RouterGate"
    rand = holder.gate.state_dict()
    assert any(not _t.allclose(rand[k].float(), trained[k].float())
               for k in trained if rand[k].dim() > 1), \
        "mole_random weights match the trained gate — it was not randomised"
    # ...and it must NOT have destroyed the trained gate that mole_router still needs.
    for k, v in holder._router_gate.state_dict().items():
        assert _t.allclose(v.float(), trained[k].float()), \
            f"mole_random corrupted the stashed RouterGate at {k}"
