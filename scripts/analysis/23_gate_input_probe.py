#!/usr/bin/env python
"""Step 0 of the gate fix: is condition identity even PRESENT in what the gate reads?

    PYTHONPATH=src python scripts/analysis/23_gate_input_probe.py --n-programs 200
    PYTHONPATH=src python scripts/analysis/23_gate_input_probe.py --smoke   # 12 programs, 4 layers

WHY THIS RUNS BEFORE ANY GATE RETRAIN
-------------------------------------
MASTER_REPORT §12.8 measured that the RouterLoRA gate ignores its input: one fixed blend on
every condition (total-variation distance .011-.056 from the grand mean), three of eight
experts dead, composites 13-60x BELOW chance on the experts whose transforms are present.
§12.9 gives two candidate causes, and they call for different fixes:

  * a TRAINING failure — the signal is in the residual stream and the objective never asked
    the gate to use it (no load-balancing term, no entropy regulariser, no routing
    supervision). Fix with the auxiliary losses in `configs/mole/routerlora_balanced.yaml`.
  * a REPRESENTATION failure — condition identity is not linearly available at the layer
    inputs the gate reads, in which case no loss function helps and the fix is a different
    gate INPUT (pooled sequence state, explicit features).

A linear probe separates them, and it costs one forward pass per program. Running the
retrain first would be spending 3 GPU-h to test a hypothesis this settles for a fraction of
that.

WHAT IS PROBED, AND WHY IT MATCHES THE GATE
-------------------------------------------
`mole/model.py`'s hook reads each decoder layer's INPUT hidden state and hands it to the
gate. So the probe reads exactly that: `output_hidden_states=True` gives `hidden_states[i]`
as the input to layer `i`. Prompts are rendered through `obtune.prompts`, the frozen builder
every other arm uses, so the distribution matches what the gate saw at train and eval time
(CLAUDE.md §4 silent-failure #3).

The BASE model is used, not the mixture. The question is whether the signal is available in
the residual stream at all; probing through an attached gate would make the measurement
depend on the very component under test.

Pooling is mean-over-real-tokens. The gate decides per token, so a pooled probe is the
GENEROUS test: if the condition cannot be decoded even from the whole sequence, it certainly
cannot be decoded from a single token, and a per-token gate is hopeless. A pooled probe that
succeeds does not by itself prove per-token routing is easy — that asymmetry is stated here
rather than glossed.

DISCIPLINE
----------
* **H1 is never loaded.** It is the held-out family; a probe read would spend quarantine
  budget to answer a question about the TRAINABLE conditions. Conditions are the six with
  Grid A variants (S3/S4 have testset variants only).
* **Splits partition by `program_id`, never by row** (§4 silent-failure #1). Every condition
  of one program is a near-duplicate of the others; splitting by row would put a program's
  L1r variant in train and its L2 variant in test and report a wildly inflated accuracy.
* One item per program, so no program contributes more rows than another.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
OUT = ROOT / "results" / "analysis" / "gate_input_probe.json"


def fit_probe(X, y, n_classes, *, epochs=300, lr=0.05, wd=1e-3, seed=17):
    """Multinomial logistic regression in torch.

    sklearn is not in the pinned environment (`env/lock-obtune.txt`) and a probe is not worth
    unpinning it for. Features are standardised with TRAIN statistics only — using the full
    set's mean/std would leak test information into the fit and inflate the accuracy, which
    is the classic way a probe result becomes meaningless.
    """
    import torch

    g = torch.Generator().manual_seed(seed)
    mu, sd = X[0].mean(0, keepdim=True), X[0].std(0, keepdim=True).clamp_min(1e-6)
    Xtr, Xte = (X[0] - mu) / sd, (X[1] - mu) / sd
    ytr, yte = y
    W = torch.zeros(Xtr.shape[1], n_classes, requires_grad=True)
    b = torch.zeros(n_classes, requires_grad=True)
    torch.nn.init.normal_(W, std=0.01, generator=g)
    opt = torch.optim.AdamW([W, b], lr=lr, weight_decay=wd)
    for _ in range(epochs):
        opt.zero_grad()
        torch.nn.functional.cross_entropy(Xtr @ W + b, ytr).backward()
        opt.step()
    with torch.no_grad():
        pred = (Xte @ W + b).argmax(-1)
        acc = float((pred == yte).float().mean())
        per_class = {}
        for c in range(n_classes):
            m = yte == c
            per_class[c] = float((pred[m] == c).float().mean()) if int(m.sum()) else float("nan")
    return acc, per_class, pred


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="qwen25c-1.5b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--n-programs", type=int, default=200)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--smoke", action="store_true", help="12 programs, every 8th layer")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    if args.smoke:
        args.n_programs = 12

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from obtune import data, prompts
    from obtune.config import load_config
    from obtune.seedutil import set_seed

    set_seed(17)
    hf_id = load_config("models.yaml")["models"][args.model]["hf_id"]
    tok = AutoTokenizer.from_pretrained(hf_id)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token

    # One item per program per condition, restricted to programs present in EVERY condition
    # so the probe cannot exploit "this program only appears as L1r".
    by_cond: dict[str, dict[str, object]] = {}
    for c in CONDS:
        items = data.load_eval_items([c], args.language, source="heldout")
        first: dict[str, object] = {}
        for it in items:
            first.setdefault(it.program_id, it)
        by_cond[c] = first
    common = sorted(set.intersection(*(set(v) for v in by_cond.values())))
    common = common[: args.n_programs]
    print(f"[probe] {len(common)} programs x {len(CONDS)} conditions "
          f"= {len(common)*len(CONDS)} sequences")

    texts, labels, pids = [], [], []
    for ci, c in enumerate(CONDS):
        for pid in common:
            it = by_cond[c][pid]
            texts.append(prompts.render_chat(
                prompts.build_prompt(code=it.code, entry_point=it.entry_point,
                                     args_repr=it.args_repr, language=it.language,
                                     condition=it.condition, oracle=False,
                                     one_shot=False, demo=None), tok))
            labels.append(ci)
            pids.append(pid)

    model = AutoModelForCausalLM.from_pretrained(hf_id, dtype=torch.bfloat16, device_map=None)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(dev).eval()

    n_layers = model.config.num_hidden_layers
    keep = list(range(0, n_layers, 8)) if args.smoke else list(range(n_layers))
    feats = {l: [] for l in keep}
    with torch.no_grad():
        for i in range(0, len(texts), args.batch):
            enc = tok(texts[i:i + args.batch], return_tensors="pt", padding=True,
                      truncation=True, max_length=2048).to(dev)
            hs = model(**enc, output_hidden_states=True).hidden_states
            m = enc["attention_mask"].unsqueeze(-1).float()
            for l in keep:
                # hidden_states[l] is the INPUT to decoder layer l — exactly what the gate's
                # forward_pre_hook receives. Mean over real tokens only; padding would drag
                # every sequence toward the pad embedding and blur the classes.
                pooled = (hs[l].float() * m).sum(1) / m.sum(1).clamp_min(1e-6)
                feats[l].append(pooled.cpu())
            if (i // args.batch) % 20 == 0:
                print(f"[probe]   {i+len(enc['input_ids'])}/{len(texts)}", flush=True)

    # PROGRAM-DISJOINT split (§4 silent-failure #1).
    uniq = sorted(set(pids))
    cut = int(0.7 * len(uniq))
    train_p = set(uniq[:cut])
    idx_tr = [i for i, p in enumerate(pids) if p in train_p]
    idx_te = [i for i, p in enumerate(pids) if p not in train_p]
    y = torch.tensor(labels)
    ytr, yte = y[idx_tr], y[idx_te]
    print(f"[probe] split: {len(train_p)} train programs / {len(uniq)-len(train_p)} test "
          f"({len(idx_tr)} / {len(idx_te)} sequences), chance = {1/len(CONDS):.3f}")

    art = {"model": args.model, "language": args.language, "conditions": CONDS,
           "n_programs": len(common), "chance": 1.0 / len(CONDS),
           "n_train_programs": len(train_p), "n_test_programs": len(uniq) - len(train_p),
           "layers": {}}
    print(f"\n{'layer':>6s}{'probe acc':>11s}{'vs chance':>11s}   per-condition recall")
    for l in keep:
        X = torch.cat(feats[l], 0)
        acc, per_class, _ = fit_probe((X[idx_tr], X[idx_te]), (ytr, yte), len(CONDS))
        art["layers"][str(l)] = {"accuracy": acc,
                                 "per_condition_recall": {CONDS[k]: v for k, v in per_class.items()}}
        rec = "  ".join(f"{CONDS[k]}={v:.2f}" for k, v in per_class.items())
        print(f"{l:6d}{acc:11.3f}{acc - 1/len(CONDS):+11.3f}   {rec}")

    best = max(art["layers"].items(), key=lambda kv: kv[1]["accuracy"])
    art["best_layer"] = int(best[0])
    art["best_accuracy"] = best[1]["accuracy"]
    print(f"\nbest layer {best[0]}: {best[1]['accuracy']:.3f} (chance {1/len(CONDS):.3f})")
    print("VERDICT:", "signal IS present -> the gate is a TRAINING failure (fixes 1-3)"
          if art["best_accuracy"] > 2.0 / len(CONDS)
          else "signal is WEAK -> suspect a REPRESENTATION failure (fix 4: change the gate input)")

    out = Path(args.out) if args.out else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(art, indent=2))
    print(f"artifact -> {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
