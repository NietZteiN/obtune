#!/usr/bin/env python
"""Master tables as markdown: per-model forward/backward grid, models, dataset, taxonomy.

    python scripts/analysis/59_master_tables.py            # writes docs/MASTER_TABLES.md, prints it

Numbers come from results/cells/*/cell_meta.json accuracies (forward from panel_core and the
composite phases, backward from inverse_generic, in-context from basecheck_1shot) and from the
configs and data files -- nothing is typed by hand. Cells that do not exist yet render as `--`,
so the table is honest about coverage and fills in as jobs land.
"""
from __future__ import annotations
import json, collections, datetime as dt
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT/"src"))
from obtune.config import load_config
CELLS = ROOT/"results/cells"
MODELS = ["codellama-7b","codellama-13b","codellama-34b","llama31-8b","starcoder2-15b","gemma3-12b","codegemma-7b","granite31-8b"]
NICE = {"codellama-7b":"CodeLlama-7B","codellama-13b":"CodeLlama-13B","codellama-34b":"CodeLlama-34B","llama31-8b":"Llama-3.1-8B",
        "starcoder2-15b":"StarCoder2-15B","gemma3-12b":"Gemma-3-12B","codegemma-7b":"CodeGemma-7B","granite31-8b":"Granite-3.1-8B"}
LADDER = ["L0","L1b","L1r","L2","S1","S2","X1"]
SEEN_STACKS = ["C_L1b_S1","C_L1r_S1","C_S1_L1r","C_L2_S4","C_L1r_S3","C_S4_S3"]
UNSEEN_STACKS = ["C_L1r_X1","C_X1_S1","C_S2_X1"]
INTERV = [("ICL (1-shot)","base_1shot"),("LoRA clean","tuned_L0"),("breadth","mono_all"),("anchored","cons_lam3"),("family","tuned_X1")]
FWD_PH = {"ladder":["panel_core"],"seen":["composite_generic"],"unseen":["f2_divergence"]}

def acc(phases, m, s, c):
    for ph in phases:
        p = CELLS/ph/m/"python"/f"{s}__{c}"/"cell_meta.json"
        if p.exists():
            d = json.loads(p.read_text()); return d.get("accuracy"), d.get("format_fail_rate")
    return None, None

FMT_MAX = 0.25   # the inverse design's pre-registered gate; the ICL read uses the same bar

def pooled(phases, m, s, conds):
    """Mean accuracy over conds, or None if any cell is missing, or "fmt" if any cell fails the
    format gate. A cell whose responses are mostly unparseable measures the prompt contract, not
    the task: on 2026-09-13 twenty of thirty-five backward cells on the new panel models were
    over the bar (CodeGemma anchored 0.989), and averaging them produced a -20 point "backward
    cost" that was format collapse wearing a competence number."""
    pairs = [acc(phases, m, s, c) for c in conds]
    if any(a is None for a, _ in pairs): return None
    if any((ff or 0) > FMT_MAX for _, ff in pairs): return "fmt"
    return sum(a for a, _ in pairs)/len(pairs)

def f(x, kind="acc"):
    if x is None: return "--"
    if x == "fmt": return "fmt"
    return f"{x:.3f}" if kind == "acc" else f"{x*100:+.1f}"

out = []
out.append(f"# Master tables\n\n*Generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC by `scripts/analysis/59_master_tables.py`. "
           "Every number is read from a cell or a config; `--` means the cell does not exist yet.*\n")

# ---------------- 1. per-model master grid ----------------
out.append("## 1. Master grid — every model × every obfuscation type, forward and backward\n")
out.append("Forward = output prediction (the task adapters were trained on). Backward = input prediction on the "
           "same programs, graded by execution; no adapter is trained on it. `base` columns are the untuned "
           "model's accuracy; every intervention column is its **change in points vs base** in that direction. "
           "In-context learning has no backward run. Stacks have no backward run. **`fmt`** marks a cell whose "
           "format-failure rate exceeds 0.25: its responses are mostly unparseable, so it measures the prompt "
           "contract rather than the task and is excluded from every mean. The backward task and the in-context "
           "run both use a one-shot template written for CodeLlama-7B, which passes the gate on every cell; most "
           "of the other panel models do not.\n")
hdr = "| condition | base fwd | base bwd | ICL Δf | LoRA-clean Δf | Δb | breadth Δf | Δb | anchored Δf | Δb | family Δf | Δb |"
sep = "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
summary = collections.defaultdict(list)
for m in MODELS:
    out.append(f"\n### {NICE[m]}\n"); out.append(hdr); out.append(sep)
    rows = [(c, "ladder", [c]) for c in LADDER] + [("seen stacks (6)","seen",SEEN_STACKS), ("unseen-containing stacks (3)","unseen",UNSEEN_STACKS)]
    for label, kind, conds in rows:
        bf = pooled(FWD_PH[kind], m, "base", conds)
        bb = pooled(["inverse_generic"], m, "base", conds) if kind == "ladder" else None
        cells = [label, f(bf), f(bb)]
        for name, sysname in INTERV:
            if sysname == "base_1shot":
                a = pooled(["basecheck_1shot"], m, sysname, conds) if (kind=="ladder" and conds[0]!="X1") else None
                cells.append(f(None if (a is None or bf is None) else ("fmt" if "fmt" in (a, bf) else a-bf), "d")); continue
            af = pooled(FWD_PH[kind], m, sysname, conds); ab = pooled(["inverse_generic"], m, sysname, conds) if kind=="ladder" else None
            g = lambda a, b: (None if (a is None or b is None) else ("fmt" if ("fmt" in (a, b)) else a-b))
            df_, db_ = g(af, bf), g(ab, bb)
            cells += [f(df_,"d"), f(db_,"d")]
            if kind=="ladder" and conds[0]=="L0": summary[(name,"clean fwd")].append(df_); summary[(name,"clean bwd")].append(db_)
            if kind=="ladder" and conds[0] in ("L1b","L1r","L2","S1","S2"): summary[(name,"obf fwd")].append(df_); summary[(name,"obf bwd")].append(db_)
            if kind=="ladder" and conds[0]=="X1": summary[(name,"unseen fwd")].append(df_); summary[(name,"unseen bwd")].append(db_)
        out.append("| " + " | ".join(cells) + " |")

out.append("\n### Cross-model summary — mean change vs the untuned model, in points\n")
out.append("| intervention | clean fwd | clean bwd | seen-obf fwd | seen-obf bwd | unseen-family fwd | unseen-family bwd |")
out.append("|---|---:|---:|---:|---:|---:|---:|")
for name,_ in INTERV[1:]:
    def mean(k):
        allv=[x for x in summary[(name,k)] if x is not None]; v=[x for x in allv if x != "fmt"]; g=len(allv)-len(v)
        return (f"{sum(v)/len(v)*100:+.1f} (n={len(v)}" + (f", {g} fmt)" if g else ")")) if v else (f"-- ({g} fmt)" if g else "--")
    out.append(f"| {name} | {mean('clean fwd')} | {mean('clean bwd')} | {mean('obf fwd')} | {mean('obf bwd')} | {mean('unseen fwd')} | {mean('unseen bwd')} |")

# ---------------- 2. models ----------------
mm = load_config("models.yaml")["models"]
out.append("\n## 2. Models\n")
out.append("| model | HF id | lineage | type | layers | hidden | chat template | role |")
out.append("|---|---|---|---|---:|---:|---|---|")
for k in MODELS + ["llama31-8b-base"]:
    v = mm[k]; origin = v.get("origin") or ("Meta" if "llama" in k else "?")
    out.append(f"| {NICE.get(k,k)} | `{v['hf_id']}` | {origin.split(' ')[0]} | {v.get('family')} | {v.get('n_layers')} | {v.get('hidden_size')} | {v.get('render_mode') or 'system'} | {v.get('role')} |")
out.append("\n`chat template`: `system` = accepts a system role; `merged` = system text folded into the user turn; `plain` = no chat template (pretrained checkpoint, one-shot only). Qwen models are excluded by scope rule.")

# ---------------- 3. dataset ----------------
src = collections.Counter(); cases=[]; loc=[]
for l in (ROOT/"data/train/base/python.jsonl").open():
    r=json.loads(l); src[r["source"]]+=1; cases.append(len(r["cases"])); loc.append(r.get("loc",0))
sp = json.loads((ROOT/"data/splits/python.json").read_text())
def n_prog(c): 
    p=ROOT/f"data/eval/heldout/items/{c}/python.jsonl"; return len({json.loads(l)["program_id"] for l in p.open()}) if p.exists() else None
out.append("\n## 3. Dataset\n")
out.append("| property | value |"); out.append("|---|---|")
out.append(f"| base programs (Python) | {sum(src.values())} — " + ", ".join(f"{k} {v}" for k,v in src.most_common()) + " |")
out.append(f"| split | by `program_id`, seed {sp['seed']}: train {sp['n_train']} / val {sp['n_val']} / test (held-out eval) {sp['n_test']} |")
out.append(f"| input cases per program | {sum(cases)/len(cases):.0f} (fixed), gold output executed from the clean parent |")
out.append(f"| program length | mean {sum(loc)/len(loc):.1f} LOC |")
out.append(f"| held-out eval items, clean (L0) | {n_prog('L0')} programs × 3 cases |")
out.append(f"| coverage per condition (programs) | L1b {n_prog('L1b')} · S1 {n_prog('S1')} · X1 {n_prog('X1')} · C_L1r_S1 {n_prog('C_L1r_S1')} · C_L1r_X1 {n_prog('C_L1r_X1')} — structural transforms decline some programs by design; the unseen family needs ≥3 sites |")
out.append(f"| paired contrasts | run on the program subset common to every cell, recorded before evaluation |")
out.append(f"| JavaScript | {n_prog.__globals__['json'] and len({json.loads(l)['program_id'] for l in (ROOT/'data/eval/heldout/items/L0/javascript.jsonl').open()})} held-out programs; corpus transferred intact, cannot be regenerated (no `node` on the cluster) |")
out.append("| grading | strict normalised exact match, no containment; backward task graded by executing the produced call |")

# ---------------- 4. taxonomy ----------------
cond = load_config("conditions.yaml")["conditions"]
if isinstance(cond, list): cond = {c["code"]: c for c in cond}
comp = load_config("conditions_composite.yaml")["composite_conditions"]
out.append("\n## 4. Obfuscation taxonomy\n")
out.append("Single transforms are applied to the clean parent, never stacked, with identical semantics across languages. Stacks live in a separate namespace.\n")
out.append("| code | family | transform | trainable | role in the paper |")
out.append("|---|---|---|---|---|")
ROLE = {"L0":"clean reference","L1b":"ladder","L1r":"ladder","L2":"ladder","S1":"ladder","S2":"ladder",
        "S3":"depth-3/4 stacks only","S4":"depth-3/4 stacks only","X1":"**unseen family** (trainable sibling of H1; every unseen-family number)",
        "X1m":"mechanism half of X1","X1s":"mechanism half of X1","X2":"second family, trainable","Y2":"second family, eval-only",
        "H1":"quarantined; evaluation budget spent, never stacked"}
for k in ["L0","L1b","L1r","L2","S1","S2","S3","S4","X1","X1m","X1s","H1"]:
    v = cond[k]; d = " ".join(str(v.get("description","")).split())
    d = d.split(". ")[0][:95]
    out.append(f"| {k} | {v.get('family')} | {d} | {'yes' if v.get('trainable') else 'no'} | {ROLE.get(k,'')} |")
out.append("\n**Stacked composites** (order matters; composition does not commute):\n")
out.append("| code | composition | contains unseen family | used in |"); out.append("|---|---|---|---|")
for k,v in comp.items():
    parts = " → ".join(v["parts"]); unseen = "yes" if any(p.startswith("X1") for p in v["parts"]) else "no"
    where = "divergence ladder (RQ4)" if unseen=="yes" else ("depth-3/4 stacks" if k.startswith(("C3","C4")) else "seen stacks (RQ1)")
    out.append(f"| {k} | {parts} | {unseen} | {where} |")

md = "\n".join(out) + "\n"
(ROOT/"docs/MASTER_TABLES.md").write_text(md); print(md)
