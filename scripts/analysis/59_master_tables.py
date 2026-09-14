#!/usr/bin/env python
"""Master tables: per-model forward/backward grid over every condition and every stack, models,
dataset, obfuscation taxonomy. Emits markdown (docs/MASTER_TABLES.md) and LaTeX
(paper/router_merger/tables/master_*.tex, setup_*.tex) from the same cells.

    python scripts/analysis/59_master_tables.py

Numbers come from results/cells/*/cell_meta.json (forward: panel_core, composite_generic,
composite_depth, f2_divergence; backward: inverse_generic; in-context: basecheck_1shot) and from
the configs and data files -- nothing is typed by hand. Cells that do not exist yet render as `--`.

Three numbers per (system, condition, direction):
  acc   raw accuracy of that system on that condition
  d     change in points against the untuned model on the same condition
  %     acc as a percentage of the untuned model's CLEAN-CODE accuracy in the same direction --
        "how much of the original accuracy the system brings back". The untuned model on clean
        code is 100 by definition; on obfuscated code it shows what the obfuscation removed; an
        intervention above 100 has more than restored it.
"""
from __future__ import annotations
import json, collections, datetime as dt, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT/"src")); sys.path.insert(0, str(ROOT/"scripts"/"analysis"))
from obtune.config import load_config
from cellkit import meta_path, trials_path  # backward cells: prefer the v2 (newline-stop) grade where it exists
CELLS = ROOT/"results/cells"
TEX_OUT = ROOT/"paper/router_merger/tables"
MODELS = ["codellama-7b","codellama-13b","codellama-34b","llama31-8b","starcoder2-15b","gemma3-12b","codegemma-7b","granite31-8b"]
NICE = {"codellama-7b":"CodeLlama-7B","codellama-13b":"CodeLlama-13B","codellama-34b":"CodeLlama-34B","llama31-8b":"Llama-3.1-8B",
        "starcoder2-15b":"StarCoder2-15B","gemma3-12b":"Gemma-3-12B","codegemma-7b":"CodeGemma-7B","granite31-8b":"Granite-3.1-8B",
        "llama31-8b-base":"Llama-3.1-8B (base)"}
PARAMS_B = {"codellama-7b":6.7,"codellama-13b":13.0,"codellama-34b":33.7,"llama31-8b":8.0,"starcoder2-15b":15.5,
            "gemma3-12b":12.2,"codegemma-7b":8.5,"granite31-8b":8.2,"llama31-8b-base":8.0}  # nominal, from the model cards
LADDER = ["L0","L1b","L1r","L2","S1","S2","X1"]
SEEN_STACKS = ["C_L1b_S1","C_L1r_S1","C_S1_L1r","C_L2_S4","C_L1r_S3","C_S4_S3"]
DEPTH_STACKS = ["C3_L1r_S3_S4","C3_S1_S3_S4","C3_L1r_S1_S4","C4_L1r_S1_S3_S4"]
UNSEEN_STACKS = ["C_L1r_X1","C_X1_S1","C_S2_X1"]
HALF_STACKS = ["C_L1r_X1m","C_S1_X1s"]
D3_STACKS = ["C3_L1r_S1_X1"]
INTERV = [("ICL","base_1shot"),("clean LoRA","tuned_L0"),("breadth","mono_all"),("anchored","cons_lam3"),("family","tuned_X1")]
PHASES = {"ladder":["panel_core"],"seen":["composite_generic"],"depth":["composite_depth","composite_generic"],
          "unseen":["f2_divergence"],"half":["f2_divergence"],"d3":["f2_divergence"]}
KIND = {}
for c in LADDER: KIND[c]="ladder"
for c in SEEN_STACKS: KIND[c]="seen"
for c in DEPTH_STACKS: KIND[c]="depth"
for c in UNSEEN_STACKS: KIND[c]="unseen"
for c in HALF_STACKS: KIND[c]="half"
for c in D3_STACKS: KIND[c]="d3"
FMT_MAX = 0.25   # the inverse design's pre-registered gate; the ICL read uses the same bar

def acc(phases, m, s, c):
    for ph in phases:
        p = meta_path(CELLS/ph/m/"python"/f"{s}__{c}")
        if p.exists():
            d = json.loads(p.read_text()); return d.get("accuracy"), d.get("format_fail_rate")
    return None, None

def pooled(phases, m, s, conds):
    """Mean accuracy over conds; None if any cell is missing; "fmt" if any cell fails the format gate.
    A cell whose responses are mostly unparseable measures the prompt contract, not the task: on
    2026-09-13 twenty of thirty-five backward cells on the new panel models were over the bar
    (CodeGemma anchored 0.989), and averaging them produced a -20 point "backward cost" that was
    format collapse wearing a competence number. Applied PER CELL, which is stricter than the
    pooled registration and marks four CodeLlama-7B backward cells the pooled rate passes."""
    pairs = [acc(phases, m, s, c) for c in conds]
    if any(a is None for a, _ in pairs): return None
    if any((ff or 0) > FMT_MAX for _, ff in pairs): return "fmt"
    return sum(a for a, _ in pairs)/len(pairs)

def fwd(m, s, conds): return pooled(PHASES[KIND[conds[0]]], m, s, conds)
# The `ladder` guard here was correct until 2026-09-13 and wrong after it: inverse_stacks.yaml
# writes the stacks into the SAME phase, so the guard was hiding cells that exist on disk.
# PHASE ORDER MATTERS. inverse_1shot holds the ladder re-read with the SAME one-shot prompt the
# stacks and the merges always used; inverse_generic holds the original ladder read, which was
# zero-shot on the seven non-7B models (prompt_id inverse_v1 against inverse_1shot_v1). First hit
# wins, so a model with the repair reads one-shot everywhere and a model without it is unchanged.
BWD_PH = ["inverse_1shot", "inverse_generic"]
def bwd(m, s, conds): return pooled(BWD_PH, m, s, conds)
def icl(m, conds): return pooled(["basecheck_1shot"], m, "base_1shot", conds) if (KIND[conds[0]]=="ladder" and conds[0]!="X1") else None

def triple(a, b, ref):
    """(acc, delta, pct) for system accuracy a against base accuracy b and clean-base reference ref."""
    if a is None: return (None, None, None)
    if a == "fmt": return ("fmt","fmt","fmt")
    d = None if b is None else ("fmt" if b == "fmt" else a-b)          # no delta against a base that produced nothing parseable
    p = None if ref is None else ("fmt" if (ref == "fmt" or ref == 0) else a/ref*100)
    return (a, d, p)

def fa(x): return "--" if x is None else ("fmt" if x=="fmt" else f"{x:.3f}")
def fd(x): return "--" if x is None else ("fmt" if x=="fmt" else f"{x*100:+.1f}")
def fp(x): return "--" if x is None else ("fmt" if x=="fmt" else f"{x:.0f}")
def ta(x): return "--" if x is None else ("fmt" if x=="fmt" else f"{x:.3f}")
def td(x): return "--" if x is None else ("fmt" if x=="fmt" else f"${x*100:+.1f}$")
def tp(x): return "--" if x is None else ("fmt" if x=="fmt" else f"{x:.0f}")
def tex_esc(s): return s.replace("_", r"\_")

ROWS = ([(c, [c]) for c in LADDER] + [(c,[c]) for c in SEEN_STACKS] + [("seen stacks, pooled (6)", SEEN_STACKS)]
        + [(c,[c]) for c in DEPTH_STACKS] + [("depth-3/4 stacks, pooled (4)", DEPTH_STACKS)]
        + [(c,[c]) for c in UNSEEN_STACKS] + [("unseen-containing stacks, pooled (3)", UNSEEN_STACKS)]
        + [(c,[c]) for c in HALF_STACKS] + [(c,[c]) for c in D3_STACKS])

def model_grid(m):
    """Returns list of dict rows: label, dir, base(acc,pct), per-intervention triples."""
    refF = fwd(m, "base", ["L0"]); refB = bwd(m, "base", ["L0"])
    rows = []
    for label, conds in ROWS:
        bf = fwd(m, "base", conds)
        r = {"label": label, "dir": "fwd", "base": triple(bf, bf, refF)[::2], "iv": {}}
        for name, sysn in INTERV:
            a = icl(m, conds) if sysn=="base_1shot" else fwd(m, sysn, conds)
            r["iv"][name] = triple(a, bf, refF)
        rows.append(r)
    # The backward block used to stop at the ladder, because that is all inverse_generic held.
    # It now carries the stacks too (configs/eval/inverse_stacks.yaml, 2026-09-13), so it uses
    # the SAME row list as the forward block -- the two halves of the table line up row for row,
    # which is the whole point of putting them under one heading.
    for label, conds in ROWS:
        bb = bwd(m, "base", conds)
        r = {"label": label, "dir": "bwd", "base": triple(bb, bb, refB)[::2], "iv": {}}
        for name, sysn in INTERV:
            a = None if sysn=="base_1shot" else bwd(m, sysn, conds)
            r["iv"][name] = triple(a, bb, refB)
        rows.append(r)
    return rows

GRIDS = {m: model_grid(m) for m in MODELS}

# ---------------- summary buckets ----------------
BUCKET = {"L0":"clean","L1b":"seen","L1r":"seen","L2":"seen","S1":"seen","S2":"seen","X1":"unseen family"}
for c in SEEN_STACKS+DEPTH_STACKS: BUCKET[c]="seen stacks"
for c in UNSEEN_STACKS+D3_STACKS: BUCKET[c]="unseen-containing stacks"
SUMMARY = collections.defaultdict(list)   # (interv, bucket, dir) -> [(d, p)]
for m in MODELS:
    for r in GRIDS[m]:
        b = BUCKET.get(r["label"])
        if b is None: continue
        for name, t in r["iv"].items():
            if t[0] is not None: SUMMARY[(name, b, r["dir"])].append((t[1], t[2]))

def summ_parts(name, b, d):
    """(mean delta pts, n, fmt) and (mean pct, n, fmt), each over its own numeric cells: a delta is gated
    when the untuned cell on the same condition is, a percentage when the clean-code reference is."""
    v = SUMMARY[(name, b, d)]
    dv = [x[0] for x in v if isinstance(x[0], float)]; gd = sum(1 for x in v if x[0] == "fmt")
    pv = [x[1] for x in v if isinstance(x[1], float)]; gp = sum(1 for x in v if x[1] == "fmt")
    return ((sum(dv)/len(dv)*100 if dv else None, len(dv), gd), (sum(pv)/len(pv) if pv else None, len(pv), gp))

def _n(n, g): return f"n={n}" + (f", {g} fmt" if g else "")
def summ(name, b, d, tex=False):
    (md, nd, gd), (mp, np_, gp) = summ_parts(name, b, d)
    if md is None and mp is None: return ("-- {\\scriptsize(" + _n(0, gd) + ")}" if tex else f"-- ({_n(0,gd)})") if gd else "--"
    sd = ("--" if md is None else (f"${md:+.1f}$" if tex else f"{md:+.1f}"))
    sp = ("--" if mp is None else (f"{mp:.0f}\\%" if tex else f"{mp:.0f}%"))
    small = (lambda t: "{\\scriptsize(" + t + ")}") if tex else (lambda t: f"({t})")
    if (nd, gd) == (np_, gp): return f"{sd} / {sp} " + small(_n(nd, gd))
    return f"{sd} " + small(_n(nd, gd)) + f" / {sp} " + small(_n(np_, gp))

# ======================================================================================
# MARKDOWN
# ======================================================================================
out = []
out.append(f"# Master tables\n\n*Generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC by `scripts/analysis/59_master_tables.py`. "
           "Every number is read from a cell or a config; `--` means the cell does not exist yet. The same script writes the LaTeX "
           "versions under `paper/router_merger/tables/`.*\n")
out.append("## 1. Master grid — every model × every condition and stack, forward and backward\n")
out.append("Forward = output prediction (what the adapters were trained on). Backward = input prediction on the same programs, "
           "graded by execution; no adapter is trained on it. Both directions now cover the same rows, ladder and stacks alike. Each system shows three numbers: "
           "**acc** (raw accuracy), **Δ** (points against the untuned model on the same condition), and **%** (accuracy as a percentage "
           "of the untuned model's clean-code accuracy in the same direction — how much of the original accuracy the system brings "
           "back; the untuned model on clean code is 100 by definition, on obfuscated code it shows what the obfuscation removed, "
           "above 100 means more than restored). In-context learning has no backward run and no X1/stack run. **`fmt`** marks a "
           "cell whose format-failure rate exceeds 0.25, and it is excluded from every mean.\n\n"
           "**Two cautions about `fmt` in the backward block, both established 2026-09-14.** First, it does NOT mean "
           "\"mostly unparseable\": that bucket holds four different failures, and on several cells the majority are replies "
           "that are exactly the gold FORWARD answer — the arm answering the other question, which is a result and not a "
           "broken template. §6 marks those `‡` rather than `†`; the per-cell decomposition is "
           "`scripts/analysis/67_backward_failure_modes.py`. Second, the earlier note here — that the backward template was "
           "written for CodeLlama-7B and fails on the other models — described a ZERO-SHOT prompt that only those seven "
           "models ever received (`inverse_core.yaml` carried no one-shot demo while every other backward config did). "
           "That is withdrawn and is being re-run into phase `inverse_1shot`; see "
           "`log/transfer/2026-09-14_two-prompts-one-phase.md`.\n")
hdr = ("| condition | base acc | base % | " + " | ".join(f"{n} acc | Δ | %" for n,_ in INTERV) + " |")
sep = "|---|---:|---:|" + "---:|---:|---:|"*len(INTERV)
for m in MODELS:
    out.append(f"\n### {NICE[m]}\n"); out.append("**Forward (output prediction)**\n"); out.append(hdr); out.append(sep)
    for r in GRIDS[m]:
        if r["dir"] == "bwd": continue
        lab = f"*{r['label']}*" if "pooled" in r["label"] else r["label"]
        cells = [lab, fa(r["base"][0]), fp(r["base"][1])]
        for n,_ in INTERV: t=r["iv"][n]; cells += [fa(t[0]), fd(t[1]), fp(t[2])]
        out.append("| " + " | ".join(cells) + " |")
    out.append("\n**Backward (input prediction)**\n"); out.append(hdr); out.append(sep)
    for r in GRIDS[m]:
        if r["dir"] == "fwd": continue
        lab = f"*{r['label']}*" if "pooled" in r["label"] else r["label"]
        cells = [lab, fa(r["base"][0]), fp(r["base"][1])]
        for n,_ in INTERV: t=r["iv"][n]; cells += [fa(t[0]), fd(t[1]), fp(t[2])]
        out.append("| " + " | ".join(cells) + " |")

out.append("\n### Cross-model summary — mean Δ (points) / mean % of the untuned model's clean-code accuracy\n")
out.append("Means over the cells that exist and pass the format gate; `n` counts them, `fmt` counts the gated ones. "
           "'seen' = L1b, L1r, L2, S1, S2; 'seen stacks' = the six depth-2 and four depth-3/4 stacks of seen transforms; "
           "'unseen-containing stacks' = the three depth-2 and one depth-3 stacks with X1 inside.\n")
BUCKETS = ["clean","seen","unseen family","seen stacks","unseen-containing stacks"]
out.append("| intervention | dir | " + " | ".join(BUCKETS) + " |"); out.append("|---|---|" + "---:|"*len(BUCKETS))
for n,_ in INTERV:
    for d in ("fwd","bwd"):
        if n=="ICL" and d=="bwd": continue
        out.append(f"| {n} | {d} | " + " | ".join(summ(n,b,d) for b in BUCKETS) + " |")

# ---------------- 2. models ----------------
mm = load_config("models.yaml")["models"]
def origin(k, v): return (v.get("origin") or ("Meta" if "llama" in k else "?")).split(" (")[0]
out.append("\n## 2. Models\n")
out.append("| model | HF id | lineage | type | params (B) | layers | hidden | chat template | LoRA rank / targets | role |")
out.append("|---|---|---|---|---:|---:|---:|---|---|---|")
lora = load_config("models.yaml").get("lora", {})
lora_desc = f"r={lora.get('r','?')}, α={lora.get('alpha','?')}, {', '.join(lora.get('target_modules', [])) or '?'}" if lora else "see train configs"
for k in MODELS + ["llama31-8b-base"]:
    v = mm[k]
    out.append(f"| {NICE.get(k,k)} | `{v['hf_id']}` | {origin(k,v)} | {v.get('family')} | {PARAMS_B[k]} | {v.get('n_layers')} | {v.get('hidden_size')} | {v.get('render_mode') or 'system'} | {lora_desc} | {v.get('role')} |")
out.append("\n`chat template`: `system` = accepts a system role; `merged` = system text folded into the user turn; `plain` = no chat template "
           "(pretrained checkpoint, one-shot only). `type`: `coder` = code-specialised instruct model, `instruct` = general instruct model. "
           "Parameter counts are nominal, from the model cards. Qwen models are excluded by scope rule.")

# ---------------- 3. dataset ----------------
src = collections.Counter(); cases=[]; loc=[]; src_loc=collections.defaultdict(list)
for l in (ROOT/"data/train/base/python.jsonl").open():
    r=json.loads(l); src[r["source"]]+=1; cases.append(len(r["cases"])); loc.append(r.get("loc",0)); src_loc[r["source"]].append(r.get("loc",0))
sp = json.loads((ROOT/"data/splits/python.json").read_text())
def n_items(c, lang="python"):
    p=ROOT/f"data/eval/heldout/items/{c}/{lang}.jsonl"
    if not p.exists(): return (None, None)
    ids=set(); n=0
    for l in p.open(): ids.add(json.loads(l)["program_id"]); n+=1
    return (len(ids), n)
COV = {c: n_items(c) for c in LADDER+["S3","S4","X1m","X1s"]+SEEN_STACKS+DEPTH_STACKS+UNSEEN_STACKS+HALF_STACKS+D3_STACKS}
js = n_items("L0","javascript")
out.append("\n## 3. Dataset\n")
out.append("| property | value |"); out.append("|---|---|")
out.append(f"| base programs (Python) | {sum(src.values())}: " + ", ".join(f"{k} {v} (mean {sum(src_loc[k])/len(src_loc[k]):.1f} LOC)" for k,v in src.most_common()) + " |")
out.append(f"| split | by `program_id`, seed {sp['seed']}: train {sp['n_train']} / val {sp['n_val']} / held-out eval {sp['n_test']} programs |")
out.append(f"| input cases per program | {sum(cases)/len(cases):.0f} (fixed); gold output executed from the clean parent |")
out.append(f"| program length | mean {sum(loc)/len(loc):.1f} LOC, max {max(loc)} |")
out.append(f"| held-out eval, clean (L0) | {COV['L0'][0]} programs × 3 cases = {COV['L0'][1]} items |")
out.append(f"| held-out coverage per condition | see the taxonomy tables (programs / items column); structural transforms decline some programs by design and the unseen family needs ≥3 encodable sites |")
out.append(f"| training rows per adapter | one condition's train split × 3 cases (e.g. L0: {sp['n_train']*3}); breadth (`mono_all`) trains on all five seen conditions pooled |")
out.append(f"| paired contrasts | on the program subset common to every cell in the contrast, recorded before evaluation; program-clustered bootstrap, 2,000 resamples, seed 17 |")
out.append(f"| JavaScript | {js[0]} held-out programs ({js[1]} items); corpus transferred intact, cannot be regenerated (no `node` on the cluster) |")
out.append("| grading | strict normalised exact match, no containment; backward task graded by executing the produced call against the clean parent |")

# ---------------- 4. taxonomy ----------------
cond = load_config("conditions.yaml")["conditions"]
if isinstance(cond, list): cond = {c["code"]: c for c in cond}
comp = load_config("conditions_composite.yaml")["composite_conditions"]
DESC = {"L0":"normalised original: comments and docstrings stripped, 4-space indent",
        "L1b":"adversarial renaming of all bindings incl. the entry function, from semantic-inversion tables (max→min) and an unrelated domain vocabulary",
        "L1r":"random hex renaming of all bindings (`v_a3f2`, `f_9c1e`)",
        "L2":"sequential minification of all bindings (a, b, …, aa) plus type-annotation stripping",
        "S1":"control-flow flattening of the entry function into a dispatch loop with randomised state ids and shuffled cases",
        "S2":"opaque predicates (computed always-true/false guards) plus never-called dead helpers",
        "S3":"dead-code insertion only: 1–2 never-called module-level helpers (must be ignored)",
        "S4":"opaque predicates only: 1–3 computed guards at statement boundaries (must be reasoned about)",
        "X1":"every string literal through an inline XOR decoder, every + − ^ through a type-guarded algebraic identity, int literals expanded",
        "X1m":"X1's arithmetic half only (`mechanisms: [mba]`)",
        "X1s":"X1's string half only (`mechanisms: [str]`); site bar 1",
        "H1":"string encoding (base64 / RC4 string array) plus guarded mixed-boolean-arithmetic rewriting"}
ROLE = {"L0":"clean reference","L1b":"ladder","L1r":"ladder","L2":"ladder","S1":"ladder","S2":"ladder",
        "S3":"depth-3/4 stacks and C_L1r_S3","S4":"depth-3/4 stacks, C_L2_S4, C_S4_S3","X1":"**the unseen family**: trainable sibling of H1 (r = 0.9992), every unseen-family number",
        "X1m":"mechanism ablation","X1s":"mechanism ablation","H1":"quarantined; evaluation budget spent; never stacked, never read"}
def cov(c): p,n = COV.get(c,(None,None)); return "--" if p is None else f"{p} / {n}"
out.append("\n## 4. Obfuscation taxonomy\n")
out.append("### 4a. Single transforms\n")
out.append("Applied to the clean parent, never stacked, identical semantics across languages. `size cap` is the maximum growth factor over the parent "
           "(with a character floor) above which the program is declined rather than clipped; `programs / items` is held-out coverage.\n")
out.append("| code | family | transform | trainable | size cap | programs / items | role |")
out.append("|---|---|---|---|---:|---:|---|")
for k in ["L0","L1b","L1r","L2","S1","S2","S3","S4","X1","X1m","X1s","H1"]:
    v = cond[k]
    out.append(f"| {k} | {v.get('family')} | {DESC[k]} | {'yes' if v.get('trainable') else '**never**'} | {v.get('size_cap')}× | {cov(k)} | {ROLE.get(k,'')} |")
out.append("\n### 4b. Stacked composites\n")
out.append("A separate namespace: order matters (composition does not commute), every stack is built from the clean parent by applying the parts "
           "left to right, and size caps were calibrated on a 40-program build at cap 60 (p95 × 1.25) so the cap is never the binding constraint. "
           "No stack is ever trained on; the `family` and `breadth` adapters see only single transforms.\n")
STACK_ROLE = {"C_L1r_S1":"headline identifier ⊗ structural stack","C_S1_L1r":"order control for C_L1r_S1 (renames S1's state variables)",
              "C_L1b_S1":"does L1b's specialist advantage survive stacking?","C_L2_S4":"identifier ⊗ the reason-about-it half of S2",
              "C_L1r_S3":"identifier ⊗ the ignore-it half of S2","C_S4_S3":"positive control: reconstructs S2 by composition",
              "C3_L1r_S3_S4":"depth 3, identifier first","C3_S1_S3_S4":"depth 3, structural only","C3_L1r_S1_S4":"depth 3, identifier first, flattening inside",
              "C4_L1r_S1_S3_S4":"depth 4","C_L1r_X1":"unseen family last, after renaming","C_X1_S1":"unseen material itself flattened",
              "C_S2_X1":"unseen family applied to dead code too","C_L1r_X1m":"half an unseen family (arithmetic)","C_S1_X1s":"half an unseen family (strings)",
              "C3_L1r_S1_X1":"one unseen component at depth 3"}
def group(k):
    if k in SEEN_STACKS: return "seen, depth 2 (RQ1 stacked-seen; RQ2 identifier share)"
    if k in DEPTH_STACKS: return "seen, depth 3–4 (RQ1 depth)"
    if k in UNSEEN_STACKS: return "unseen inside, depth 2 (RQ4 ladder d2)"
    if k in HALF_STACKS: return "half-unseen, depth 2 (mechanism)"
    return "unseen inside, depth 3 (RQ4 ladder d3)"
out.append("| code | parts, applied in order | depth | contains unseen family | size cap | programs / items | group | purpose |")
out.append("|---|---|---:|---|---:|---:|---|---|")
for k in SEEN_STACKS+DEPTH_STACKS+UNSEEN_STACKS+HALF_STACKS+D3_STACKS:
    v = comp[k]; parts = " → ".join(v["parts"]); unseen = "yes" if any(p.startswith("X1") for p in v["parts"]) else "no"
    out.append(f"| {k} | {parts} | {len(v['parts'])} | {unseen} | {v.get('size_cap')}× | {cov(k)} | {group(k)} | {STACK_ROLE.get(k,'')} |")

md = "\n".join(out) + "\n"
(ROOT/"docs/MASTER_TABLES.md").write_text(md); print(md)

# ======================================================================================
# LATEX
# ======================================================================================
TEX_OUT.mkdir(parents=True, exist_ok=True)
def write(name, body, source, note=""):
    hdr = (f"% GENERATED {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC by scripts/analysis/59_master_tables.py\n"
           f"% SOURCE: {source}\n% Do not edit by hand -- regenerate. {note}\n")
    (TEX_OUT/name).write_text(hdr + body + "\n"); print(f"  wrote {(TEX_OUT/name).relative_to(ROOT)}", file=sys.stderr)

SYS = {"ICL":r"ICL (\texttt{base\_1shot})","clean LoRA":r"clean LoRA (\texttt{tuned\_L0})","breadth":r"breadth (\texttt{mono\_all})",
       "anchored":r"anchored (\texttt{cons\_lam3})","family":r"family (\texttt{tuned\_X1})"}
SYS2 = {"ICL":(r"ICL",r"\texttt{base\_1shot}"),"clean LoRA":(r"clean LoRA",r"\texttt{tuned\_L0}"),"breadth":(r"breadth",r"\texttt{mono\_all}"),
        "anchored":(r"anchored",r"\texttt{cons\_lam3}"),"family":(r"family",r"\texttt{tuned\_X1}")}
COLSPEC = "@{}l" + "rr" + "|rrr"*len(INTERV) + "@{}"
def grid_tex(m):
    L = []
    L.append(r"\begin{table*}[p]"); L.append(r"\centering\scriptsize\setlength{\tabcolsep}{1.7pt}")
    L.append(r"\caption{\textbf{Master grid, " + NICE[m] + r".} Every condition and every stack, forward (output prediction) and "
             r"backward (input prediction). Per system: \emph{acc} raw accuracy; $\Delta$ points against the untuned model on the "
             r"same condition; \% accuracy as a percentage of the untuned model's clean-code accuracy in the same direction, i.e.\ how much of "
             r"the original accuracy the system brings back (100 = the untuned model on clean code). \emph{fmt}: format-failure rate above 0.25, "
             r"the cell measures the prompt contract rather than the task and enters no mean. Pooled rows average the stacks above them. "
             r"`--': cell not run.}")
    L.append(r"\label{tab:master_" + m.replace("-","") + "}")
    L.append(r"\begin{tabular}{" + COLSPEC + "}"); L.append(r"\toprule")
    mc = lambda i, txt: r"\multicolumn{3}{c" + ("|" if i < len(INTERV)-1 else "") + "}{" + txt + "}"
    L.append(r"\textbf{Condition} & \multicolumn{2}{c|}{\textbf{untuned}} & " + " & ".join(mc(i, r"\textbf{" + SYS2[n][0] + "}") for i,(n,_) in enumerate(INTERV)) + r" \\")
    L.append(r" & \multicolumn{2}{c|}{\texttt{base}} & " + " & ".join(mc(i, SYS2[n][1]) for i,(n,_) in enumerate(INTERV)) + r" \\")
    L.append(" & acc & \\% & " + " & ".join(r"acc & $\Delta$ & \%" for _ in INTERV) + r" \\")
    L.append(r"\midrule"); L.append(r"\multicolumn{" + str(3+3*len(INTERV)) + r"}{@{}l}{\emph{Forward: output prediction}} \\")
    def emit(r):
        lab = (r"\emph{" + tex_esc(r["label"]) + "}") if "pooled" in r["label"] else r"\texttt{" + tex_esc(r["label"]) + "}"
        cells = [lab, ta(r["base"][0]), tp(r["base"][1])]
        for n,_ in INTERV: t=r["iv"][n]; cells += [ta(t[0]), td(t[1]), tp(t[2])]
        L.append(" & ".join(cells) + r" \\")
    prev = None
    for r in GRIDS[m]:
        if r["dir"]=="bwd": continue
        k = KIND[r["label"]] if r["label"] in KIND else prev
        if prev is not None and k != prev and not r["label"].startswith("C_L1r_X1m"): L.append(r"\addlinespace[2pt]")
        emit(r); prev = k
    L.append(r"\midrule"); L.append(r"\multicolumn{" + str(3+3*len(INTERV)) + r"}{@{}l}{\emph{Backward: input prediction, graded by execution}} \\")
    for r in GRIDS[m]:
        if r["dir"]=="fwd": continue
        emit(r)
    L.append(r"\bottomrule"); L.append(r"\end{tabular}"); L.append(r"\end{table*}")
    return "\n".join(L)
for m in MODELS:
    write(f"master_{m.replace('-','')}.tex", grid_tex(m), "results/cells/{panel_core,composite_generic,composite_depth,f2_divergence,inverse_generic,basecheck_1shot}/"+m)

# cross-model summary
def summ_cell(name, b, d, which, tex=True):
    (md, nd, gd), (mp, np_, gp) = summ_parts(name, b, d)
    v, n, g = (md, nd, gd) if which == "d" else (mp, np_, gp)
    if v is None: return ("-- {\\scriptsize(" + f"0; {g} fmt" + ")}") if g else "--"
    val = (f"${v:+.1f}$" if which == "d" else f"{v:.0f}\\%")
    return val + " {\\scriptsize(" + f"{n}" + (f"; {g} fmt" if g else "") + ")}"
L = [r"\begin{table*}[ht]", r"\centering\footnotesize\setlength{\tabcolsep}{3pt}",
     r"\caption{\textbf{Every intervention against every kind of obfuscation, across the eight-model panel.} For each system and direction, "
     r"$\Delta$ is the mean change in points against the untuned model and \% the mean accuracy as a percentage of the untuned model's "
     r"clean-code accuracy, over the cells that exist and pass the format gate (in parentheses: the number of cells; after the semicolon, "
     r"the number gated as \emph{fmt}). Systems: ICL = \texttt{base\_1shot}, clean LoRA = \texttt{tuned\_L0}, breadth = \texttt{mono\_all}, anchored = \texttt{cons\_lam3}, family = \texttt{tuned\_X1}. "
     r"\emph{seen} = L1b, L1r, L2, S1, S2; \emph{seen stacks} = the six depth-2 and four depth-3/4 stacks "
     r"of seen transforms; \emph{unseen stacks} = the three depth-2 and one depth-3 stacks with the X1 family inside. Backward cells survive "
     r"the gate almost only on CodeLlama-7B, whose grid (Table~\ref{tab:master_codellama7b}) is the one fully interpretable backward read; "
     r"the per-model grids for the whole panel are in Appendix~\ref{app:master}.}",
     r"\label{tab:master_summary}", r"\begin{tabular}{@{}llrrrrr@{}}", r"\toprule",
     r"\textbf{System} & \textbf{measure} & \textbf{clean} & \textbf{seen} & \textbf{unseen family} & \textbf{seen stacks} & \textbf{unseen stacks} \\", r"\midrule"]
for n,_ in INTERV:
    first = True
    for d in ("fwd","bwd"):
        if n=="ICL" and d=="bwd": continue
        for which, lab in (("d", r"$\Delta$ pts"), ("p", r"\% of clean")):
            L.append((SYS2[n][0] if first else "") + f" & {d} {lab} & " + " & ".join(summ_cell(n,b,d,which) for b in BUCKETS) + r" \\")
            first = False
    if n != INTERV[-1][0]: L.append(r"\addlinespace[3pt]")
L += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
write("master_summary.tex", "\n".join(L), "results/cells (same phases as the per-model grids), all eight models")

# models table
L = [r"\begin{table*}[ht]", r"\centering\scriptsize\setlength{\tabcolsep}{2.4pt}",
     r"\caption{\textbf{The model panel.} Four lineages, code-specialised and general instruct models, 7B to 34B. \emph{Chat template}: "
     r"\emph{system} accepts a system role; \emph{merged} folds the system text into the user turn; \emph{plain} has no template and is used "
     r"for the one-shot baseline only. Parameter counts are nominal. Every adapter is a LoRA with the same rank and target modules on every model.}",
     r"\label{tab:models}", r"\begin{tabular}{@{}llllrrrl@{}}", r"\toprule",
     r"\textbf{Model} & \textbf{Checkpoint} & \textbf{Lineage} & \textbf{Type} & \textbf{Params (B)} & \textbf{Layers} & \textbf{Hidden} & \textbf{Chat template} \\", r"\midrule"]
for k in MODELS + ["llama31-8b-base"]:
    v = mm[k]
    L.append(f"{NICE[k]} & " + r"\texttt{\scriptsize " + tex_esc(v['hf_id']) + "}" + f" & {origin(k,v)} & {v.get('family')} & {PARAMS_B[k]} & {v.get('n_layers')} & {v.get('hidden_size')} & {v.get('render_mode') or 'system'} " + r"\\")
L += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
write("setup_models.tex", "\n".join(L), "configs/models.yaml")

# dataset table
L = [r"\begin{table}[ht]", r"\centering\small",
     r"\caption{\textbf{The dataset.} One Python corpus, split by program so no obfuscated variant of a training program can reach evaluation.}",
     r"\label{tab:dataset}", r"\begin{tabular}{@{}p{0.34\linewidth}p{0.6\linewidth}@{}}", r"\toprule", r"\textbf{Property} & \textbf{Value} \\", r"\midrule"]
L.append(f"Base programs (Python) & {sum(src.values())}: " + ", ".join(f"{k} {v}" for k,v in src.most_common()) + r" \\")
L.append(f"Split & by program, seed {sp['seed']}: train {sp['n_train']} / val {sp['n_val']} / held-out {sp['n_test']} " + r"\\")
L.append(f"Input cases per program & {sum(cases)/len(cases):.0f}, gold output executed from the clean parent " + r"\\")
L.append(f"Program length & mean {sum(loc)/len(loc):.1f} LOC, max {max(loc)} " + r"\\")
L.append(f"Held-out eval, clean & {COV['L0'][0]} programs $\\times$ 3 cases = {COV['L0'][1]} items " + r"\\")
L.append(r"Coverage per condition & Tables~\ref{tab:taxonomy} and \ref{tab:stacks}; structural transforms decline some programs by design, the unseen family needs $\geq 3$ encodable sites \\")
L.append(f"Training rows per adapter & one condition's train split $\\times$ 3 cases ({sp['n_train']*3}); breadth pools the five seen conditions " + r"\\")
L.append(r"Paired contrasts & on the programs common to every cell in the contrast, fixed before evaluation; program-clustered bootstrap, 2{,}000 resamples \\")
L.append(f"JavaScript & {js[0]} held-out programs ({js[1]} items), transferred intact; not regenerable on the cluster " + r"\\")
L.append(r"Grading & strict normalised exact match, no containment; the backward task executes the produced call against the clean parent \\")
L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
write("setup_dataset.tex", "\n".join(L), "data/train/base/python.jsonl, data/splits/python.json, data/eval/heldout/items/*")

# taxonomy: singles
L = [r"\begin{table*}[ht]", r"\centering\footnotesize",
     r"\caption{\textbf{Single transforms.} Each is applied to the clean parent and never stacked. \emph{Cap} is the maximum growth factor "
     r"over the parent above which a program is declined rather than clipped; \emph{programs / items} is held-out coverage. H1 is the quarantined "
     r"held-out obfuscator whose evaluation budget is spent; X1 is its trainable sibling and carries every unseen-family number.}",
     r"\label{tab:taxonomy}", r"\setlength{\tabcolsep}{3pt}\begin{tabular}{@{}llp{0.30\linewidth}lrrl@{}}", r"\toprule",
     r"\textbf{Code} & \textbf{Family} & \textbf{Transform} & \textbf{Trainable} & \textbf{Cap} & \textbf{Programs / items} & \textbf{Role} \\", r"\midrule"]
TROLE = {"L0":"clean reference","L1b":"ladder","L1r":"ladder","L2":"ladder","S1":"ladder","S2":"ladder","S3":"stacks only","S4":"stacks only",
         "X1":r"\textbf{unseen family}","X1m":"mechanism ablation","X1s":"mechanism ablation","H1":"quarantined"}
for k in ["L0","L1b","L1r","L2","S1","S2","S3","S4","X1","X1m","X1s","H1"]:
    v = cond[k]; d = DESC[k].replace("→", r"$\rightarrow$").replace("−", "$-$").replace("^", r"\^{}").replace("`","").replace("–","--")
    d = d.replace("_", r"\_")
    L.append(f"{k} & {v.get('family')} & {d} & {'yes' if v.get('trainable') else 'never'} & {v.get('size_cap')}$\\times$ & {cov(k)} & {TROLE[k]} " + r"\\")
L += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
write("setup_taxonomy.tex", "\n".join(L), "configs/conditions.yaml, data/eval/heldout/items/*")

# taxonomy: stacks
L = [r"\begin{table*}[ht]", r"\centering\footnotesize",
     r"\caption{\textbf{Stacked composites.} A separate namespace from the ladder: parts are applied to the clean parent left to right, and order "
     r"matters because composition does not commute. Size caps were calibrated on a 40-program build at cap 60 (p95 $\times$ 1.25) so that the cap "
     r"is never the binding constraint. No system is ever trained on a stack; the breadth and family adapters see single transforms only.}",
     r"\label{tab:stacks}", r"\setlength{\tabcolsep}{2.5pt}\begin{tabular}{@{}llrlrrlp{0.17\linewidth}@{}}", r"\toprule",
     r"\textbf{Code} & \textbf{Parts, in order} & \textbf{Depth} & \textbf{X1 inside} & \textbf{Cap} & \textbf{Prog.\,/\,items} & \textbf{Group} & \textbf{Purpose} \\", r"\midrule"]
TGROUP = {"seen":"seen d2","depth":"seen d3--4","unseen":"unseen d2","half":"half-unseen d2","d3":"unseen d3"}
prevk = None
for k in SEEN_STACKS+DEPTH_STACKS+UNSEEN_STACKS+HALF_STACKS+D3_STACKS:
    if prevk is not None and KIND[k] != prevk: L.append(r"\addlinespace[2pt]")
    v = comp[k]; parts = r"$\to$".join(v["parts"]); unseen = "yes" if any(p.startswith("X1") for p in v["parts"]) else "no"
    purpose = STACK_ROLE.get(k,"").replace("⊗", r"$\otimes$").replace("_", r"\_").replace("?", "?")
    L.append(r"\texttt{" + tex_esc(k) + "}" + f" & {parts} & {len(v['parts'])} & {unseen} & {v.get('size_cap')}$\\times$ & {cov(k)} & {TGROUP[KIND[k]]} & {purpose} " + r"\\")
    prevk = KIND[k]
L += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
write("setup_stacks.tex", "\n".join(L), "configs/conditions_composite.yaml, data/eval/heldout/items/*")

# ---------------- 5. routing and merging (models that have them) ----------------
ROUTING = [("router","mole_router"),("hard router","mole_hardrouter"),("uniform","mole_uniform"),("random","mole_random")]
MERGING = [("TIES","merge_ties"),("DARE-TIES","merge_dare_ties"),("DARE-linear","merge_dare_linear"),
           ("L0-anch. TIES","l0merge_ties"),("L0-anch. DARE-TIES","l0merge_dare_ties")]
R_PH = ["mole_generic"]
M_PH = ["merge_panel","rq2_generic","composite_generic","composite_depth","f2_divergence"]   # merge_panel: the 2026-09-13 panel merges
B_PH = ["merge_panel","mole_generic","rq2_generic","panel_core","composite_generic","composite_depth","f2_divergence"]
RM_ROWS = LADDER[:6] + ["X1"] + SEEN_STACKS + DEPTH_STACKS + UNSEEN_STACKS + HALF_STACKS + D3_STACKS

def rm_grid(m, systems, phases):
    refF = fwd(m, "base", ["L0"]); out = []
    for c in RM_ROWS:
        row = {"label": c, "iv": {}}
        # the untuned model on the same items: prefer the system's own phase, then the standard ones
        bf = None
        for ph in phases + B_PH:
            a, ff = acc([ph], m, "base", c)
            if a is not None: bf = "fmt" if (ff or 0) > FMT_MAX else a; break
        row["base"] = triple(bf, bf, refF)[::2]
        any_cell = False
        for name, sysn in systems:
            a = pooled(phases, m, sysn, [c]); row["iv"][name] = triple(a, bf, refF); any_cell |= a is not None
        if any_cell: out.append(row)
    return out

RM = {}
for m in MODELS:
    r = rm_grid(m, ROUTING, R_PH); g = rm_grid(m, MERGING, M_PH)
    if r or g: RM[m] = (r, g)

def rm_md(title, systems, rows):
    o = [f"\n**{title}**\n", "| condition | base acc | base % | " + " | ".join(f"{n} acc | Δ | %" for n,_ in systems) + " |",
         "|---|---:|---:|" + "---:|---:|---:|"*len(systems)]
    for r in rows:
        cells = [r["label"], fa(r["base"][0]), fp(r["base"][1])]
        for n,_ in systems: t = r["iv"][n]; cells += [fa(t[0]), fd(t[1]), fp(t[2])]
        o.append("| " + " | ".join(cells) + " |")
    return o

out.append("\n## 5. Routing and merging — every model that has them\n")
out.append("Same three numbers as §1. Routing arms are MoLE mixtures of the eight per-transform experts (L0, L1b, L1r, L2, S1, S2, S3, S4): "
           "`router` = trained gate, `hard router` = its argmax, `uniform` = fixed uniform gate, `random` = gate frozen at random init; "
           "the last two separate 'the mixture is worth something' from 'the routing is worth something'. Merges combine the specialists "
           "in weight space (TIES, DARE-TIES, DARE-linear) or anchor the merge on the clean-code adapter. Every routing cell ran through "
           "`obtune.mole.eval_mole`; the 2026-09-12 vLLM run that wrote the untuned model under these names is quarantined.\n")
for m, (r, g) in RM.items():
    out.append(f"\n### {NICE[m]}\n")
    if r: out += rm_md("Routing (forward)", ROUTING, r)
    if g: out += rm_md("Merging (forward)", MERGING, g)

md = "\n".join(out) + "\n"
(ROOT/"docs/MASTER_TABLES.md").write_text(md)

def rm_tex(m, systems, rows, kind, label):
    L = [r"\begin{table*}[p]", r"\centering\scriptsize\setlength{\tabcolsep}{1.7pt}"]
    if kind == "routing":
        cap = (r"\textbf{Routing, " + NICE[m] + r".} MoLE mixtures of the eight per-transform experts on every condition and stack that has "
               r"them: \emph{router} = trained gate, \emph{hard router} = its argmax, \emph{uniform} = fixed uniform gate, \emph{random} = gate "
               r"frozen at random initialisation. Per system: raw accuracy, $\Delta$ points against the untuned model on the same items, and "
               r"\% of the untuned model's clean-code accuracy. Every cell ran through the mixture engine.")
    else:
        cap = (r"\textbf{Merging, " + NICE[m] + r".} Weight-space merges of the per-transform specialists (TIES, DARE-TIES, DARE-linear) and "
               r"two merges anchored on the clean-code adapter, on every condition and stack that has them. Same three numbers as the master grid.")
    L.append(r"\caption{" + cap + "}"); L.append(r"\label{" + label + "}")
    L.append(r"\begin{tabular}{@{}lrr" + "|rrr"*len(systems) + "@{}}"); L.append(r"\toprule")
    mc = lambda i, txt: r"\multicolumn{3}{c" + ("|" if i < len(systems)-1 else "") + "}{" + txt + "}"
    L.append(r"\textbf{Condition} & \multicolumn{2}{c|}{\textbf{untuned}} & " + " & ".join(mc(i, r"\textbf{" + n + "}") for i,(n,_) in enumerate(systems)) + r" \\")
    L.append(r" & \multicolumn{2}{c|}{\texttt{base}} & " + " & ".join(mc(i, r"\texttt{" + tex_esc(sy) + "}") for i,(n,sy) in enumerate(systems)) + r" \\")
    L.append(" & acc & \\% & " + " & ".join(r"acc & $\Delta$ & \%" for _ in systems) + r" \\"); L.append(r"\midrule")
    prev = None
    for r in rows:
        k = KIND[r["label"]]
        if prev is not None and k != prev: L.append(r"\addlinespace[2pt]")
        cells = [r"\texttt{" + tex_esc(r["label"]) + "}", ta(r["base"][0]), tp(r["base"][1])]
        for n,_ in systems: t = r["iv"][n]; cells += [ta(t[0]), td(t[1]), tp(t[2])]
        L.append(" & ".join(cells) + r" \\"); prev = k
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
    return "\n".join(L)

for m, (r, g) in RM.items():
    mk = m.replace("-","")
    if r: write(f"master_routing_{mk}.tex", rm_tex(m, ROUTING, r, "routing", f"tab:routing_{mk}"), "results/cells/mole_generic/"+m)
    if g: write(f"master_merging_{mk}.tex", rm_tex(m, MERGING, g, "merging", f"tab:merging_{mk}"), "results/cells/{rq2_generic,composite_generic,f2_divergence}/"+m)

# ---------------- 6. ABSOLUTE master table for one model: every method x every obfuscation ----------------
# Raw accuracy only -- no deltas, no percentages (user, 2026-09-13: "I don't like this relative reporting").
ABS_SYS = [("base","base"),("ICL","base_1shot"),("clean LoRA","tuned_L0"),("breadth","mono_all"),("anchored","cons_lam3"),
           ("family","tuned_X1"),("mixture","mole_router"),("merge","merge_dare_ties")]
ABS_PH = {"base":None, "base_1shot":["basecheck_1shot"], "tuned_L0":None, "mono_all":None, "cons_lam3":None, "tuned_X1":None,
          "mole_router":["mole_generic"], "merge_dare_ties":["merge_panel","rq2_generic","composite_generic","f2_divergence"]}
ABS_ROWS = LADDER + SEEN_STACKS + DEPTH_STACKS + UNSEEN_STACKS + HALF_STACKS + D3_STACKS

def args_exact(m, sysn, c):
    """Share of items whose produced call recovers the GOLD ARGUMENTS, not merely a call that returns
    the gold value. The backward task is graded by execution and inversion is many-to-one, so
    `exchange_sort([1,2,3]) -> 0` scores as correct against any program whose answer is 0. Measured
    2026-09-13: 64-69 % of every system's backward `correct` answers are degenerate in this way, and
    the untuned model's 0.279 exec-match is 0.086 by exact arguments. Both are reported."""
    p = next((q for q in (trials_path(CELLS/ph/m/"python"/f"{sysn}__{c}") for ph in BWD_PH)
              if q.exists()), None)
    if p is None: return None
    try:
        import pandas as pd
        d = pd.read_parquet(p, columns=["args_exact"])
        return float(d["args_exact"].mean())
    except Exception:
        return None

# ---- WHY A GATED BACKWARD CELL IS GATED -------------------------------------------------------
# Until now every cell over the 0.25 format gate carried one marker, and twenty of thirty-five
# backward cells on the new panel models carry it. That collapses two different failures into one
# symbol. A reply that is exactly the program's gold RETURN VALUE is not malformed -- it is the
# answer to the FORWARD question, asked backwards, which is the paper's forward-locking claim
# showing up as a parse failure. A reply that is prose, or an expression, or three lines, is the
# prompt contract failing. The first is a result; the second is an artefact of a template written
# for CodeLlama-7B. They must not share a symbol.
#   dagger      the cell is gated and most of its replies are unparseable        -- an artefact
#   double-dag  the cell is gated and most of its replies ANSWER FORWARD         -- a result
# Measured per cell, on output_raw against the same gold the forward grader uses (63_forward_
# collapse.py established the metric). Computed ONLY for gated backward cells: it needs the trial
# rows, and reading those for every cell of every model would multiply this script's runtime.
_GOLD_CACHE = {}
_COLLAPSE_CACHE = {}

def _normed(x): return str(x).strip().strip('"').strip("'").replace(" ", "")

def _gold_for(cond):
    if cond not in _GOLD_CACHE:
        from obtune.data import load_eval_items
        try:
            _GOLD_CACHE[cond] = {(it.program_id, it.item_id): _normed(it.output_repr)
                                 for it in load_eval_items([cond], "python", source="heldout")}
        except Exception:
            _GOLD_CACHE[cond] = {}
    return _GOLD_CACHE[cond]

def collapse_rate(m, sysn, c):
    """Share of backward replies that are exactly the gold FORWARD answer. None if unreadable."""
    key = (m, sysn, c)
    if key in _COLLAPSE_CACHE: return _COLLAPSE_CACHE[key]
    p = next((q for q in (trials_path(CELLS/ph/m/"python"/f"{sysn}__{c}") for ph in BWD_PH)
              if q.exists()), None)
    val = None
    if p is not None:
        try:
            import pandas as pd
            d = pd.read_parquet(p, columns=["snippet_id", "item_id", "output_raw"])
            g = _gold_for(c)
            if g:
                hit = sum(1 for sid, iid, raw in zip(d["snippet_id"], d["item_id"], d["output_raw"])
                          if _normed(raw) == g.get((sid, iid), "\x00"))
                val = hit/len(d) if len(d) else None
        except Exception:
            val = None
    _COLLAPSE_CACHE[key] = val
    return val

def abs_cell(m, sysn, c, bwd=False):
    if bwd:
        a, ff = acc(BWD_PH, m, sysn, c)
    else:
        ph = ABS_PH.get(sysn) or PHASES[KIND[c]]
        a, ff = acc(ph, m, sysn, c)
        if a is None and ABS_PH.get(sysn) is None: a, ff = acc(B_PH, m, sysn, c)
    return a, ff

def abs_fmt(a, ff, tex=True, collapse=None):
    """`collapse` is the cell's forward-collapse rate, passed only for BACKWARD cells. A gated cell
    whose replies are mostly the gold forward answer gets the double dagger: it is forward-locking,
    not a broken template."""
    if a is None: return "--"
    gated = (ff or 0) > FMT_MAX
    if not gated: return f"{a:.3f}"
    answered_forward = collapse is not None and collapse > 0.5
    mark = (r"$^{\ddagger}$" if answered_forward else r"$^{\dagger}$") if tex else ("‡" if answered_forward else "†")
    return f"{a:.3f}{mark}"

BWD_ROWS = LADDER + SEEN_STACKS + DEPTH_STACKS + UNSEEN_STACKS + HALF_STACKS + D3_STACKS

def pct_of_base(a, b):
    """`a` as a percentage of the base model's accuracy on the SAME condition."""
    if a is None or b is None or a == "fmt" or b == "fmt" or not b: return None
    return a/b*100.0

def abs_table(m):
    ncol = 1 + 2*len(ABS_SYS)
    # arraystretch 0.92 and no inter-group spacing (2026-09-14): with the exact-arguments block gone
    # the table was still 31 pt taller than a page ("Float too large for page by 30.94pt"); 47 rows
    # at 0.92 recover ~30 pt and dropping five \addlinespace[2pt] the rest.
    L = [r"\begin{table*}[p]", r"\centering\scriptsize\setlength{\tabcolsep}{2pt}\renewcommand{\arraystretch}{0.92}",
         r"\caption{\textbf{Every method against every obfuscation, " + NICE[m] + r".} Raw accuracy (strict exact match), "
         r"with \%\,\emph{b} after each system: its accuracy as a percentage of \texttt{base}'s on the same condition. "
         r"\emph{base} is the untuned model; \emph{ICL} its one-shot prompt; \emph{clean LoRA} is tuned on unobfuscated code; "
         r"\emph{breadth} on all five seen transforms; \emph{anchored} is the paired-consistency objective; \emph{family} is trained "
         r"on the unseen family's sibling; \emph{mixture} is the learned-gate mixture of per-transform specialists; \emph{merge} is "
         r"the DARE-TIES merge of them (keys in order: \texttt{base}, \texttt{base\_1shot}, \texttt{tuned\_L0}, \texttt{mono\_all}, "
         r"\texttt{cons\_lam3}, \texttt{tuned\_X1}, \texttt{mole\_router}, \texttt{merge\_dare\_ties}). "
         r"\textbf{Backward is graded by execution}: the produced call is run against the program as shown and any call that returns the gold value is correct, because inversion is many-to-one --- 21.5\,\% of the ladder's gold return values have many valid inputs, so requiring the one recorded input would mark correct answers wrong. The stricter exact-argument rate is a secondary column in the repository's master tables. "
         r"$\dagger$: format-failure rate above 0.25, mostly replies that are not call-shaped. "
         r"$\ddagger$: format-failure rate above 0.25, but most of those replies are exactly the "
         r"gold \emph{forward} answer --- the arm answered the other question rather than failing "
         r"to parse. "
         r"`--': not run.}",
         r"\label{tab:master_abs_" + m.replace("-","") + "}",
         r"\begin{tabular}{@{}l" + "rr"*len(ABS_SYS) + "@{}}", r"\toprule",
         r"\textbf{Condition} & " + " & ".join(r"\multicolumn{2}{c}{\textbf{" + n + "}}" for n,_ in ABS_SYS) + r" \\",
         " & " + " & ".join(r"acc & \%\,b" for _ in ABS_SYS) + r" \\", r"\midrule",
         r"\multicolumn{" + str(ncol) + r"}{@{}l}{\emph{Forward: output prediction}} \\"]

    def row(c, bwd=False, strict=False):
        if strict:
            b = args_exact(m, "base", c)
            cells = []
            for _, sy in ABS_SYS:
                if sy in ("base_1shot", "mole_router"):
                    cells += ["--", "--"]; continue
                a = args_exact(m, sy, c)
                cells += ["--" if a is None else f"{a:.3f}", fp(pct_of_base(a, b))]
            return cells
        ba, bf = abs_cell(m, "base", c, bwd)
        base_ok = ba if isinstance(ba, float) and (bf or 0) <= FMT_MAX else None
        cells = []
        for _, sy in ABS_SYS:
            # `mole_router` used to be skipped here alongside `base_1shot`, because the mixture
            # had no backward cell on any model. It has a config now (mole_inverse_*.yaml), so the
            # column fills in as those land and renders `--` until then, like every other cell.
            if bwd and sy == "base_1shot":
                cells += ["--", "--"]; continue
            a, ff = abs_cell(m, sy, c, bwd)
            cr = collapse_rate(m, sy, c) if (bwd and (ff or 0) > FMT_MAX) else None
            cells += [abs_fmt(a, ff, collapse=cr), fp(pct_of_base(a if isinstance(a, float) and (ff or 0) <= FMT_MAX else None, base_ok))]
        return cells

    prev=None
    for c in ABS_ROWS:
        k=KIND[c]
        L.append(r"\texttt{" + tex_esc(c) + "} & " + " & ".join(row(c)) + r" \\"); prev=k
    L.append(r"\midrule"); L.append(r"\multicolumn{" + str(ncol) + r"}{@{}l}{\emph{Backward: input prediction, graded by execution}} \\")
    prev=None
    for c in BWD_ROWS:
        if abs_cell(m, "base", c, True)[0] is None: continue
        k=KIND[c]
        L.append(r"\texttt{" + tex_esc(c) + "} & " + " & ".join(row(c, bwd=True)) + r" \\"); prev=k
    # THE EXACT-ARGUMENTS BLOCK IS NOT EMITTED TO LATEX (user, 2026-09-14: keep the more accurate
    # grade only; the table overflowed the page at 69 rows). Execution is the accurate grade: the
    # inverse task is many-to-one -- 21.5 % of the ladder's gold return values have many valid
    # inputs -- so "exact arguments" marks a correct input wrong whenever it is not the one the
    # dataset happened to record, and reads 0.06-0.13 for every arm for that reason alone. It stays
    # in docs/MASTER_TABLES.md as the secondary column it always was.
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
    return "\n".join(L)

# One absolute table per model. The body carries CodeLlama-7B (every arm exists there); the rest go
# to the appendix and fill in as the backfill lands -- a cell that has not run renders as `--`.
for m in MODELS:
    write(f"master_abs_{m.replace('-','')}.tex", abs_table(m), "results/cells/* for " + m + " (raw accuracies, and % of base)")

# ---------------- 7. FORWARD-COLLAPSE: the mechanism table ------------------------------------
# How often each arm answers the FORWARD question when asked the BACKWARD one, pooled over every
# backward condition. This is the metric the format gate was hiding: unlike backward accuracy it is
# readable on every model and every arm, and the untuned models sit at the floor, so the whole range
# is usable. Computed by 67_backward_failure_modes.py --aggregate; read from its json here so the
# table and the analysis cannot drift apart.
#
# NOT WIRED INTO ANY SECTION. The prose is frozen pending a framing decision, so this writes the
# file and stops; nothing \inputs it until someone decides where it goes.
COLLAPSE_JSON = ROOT/"results/analysis/pipeline/backward_failure_modes_C_L1r_X1.json"
COLLAPSE_SYS = [("untuned","base"),("TIES merge","merge_ties"),("DARE-TIES merge","merge_dare_ties"),
                ("family","tuned_X1"),("clean LoRA","tuned_L0"),("breadth","mono_all"),
                ("anchored","cons_lam3"),("router","mole_router")]

def collapse_tex():
    if not COLLAPSE_JSON.exists():
        return None
    agg = json.loads(COLLAPSE_JSON.read_text()).get("aggregate")
    if not agg:
        return None
    by, means = agg["by_model"], agg["panel_mean"]
    L = [r"\begin{table}[t]", r"\centering", r"\small",
         r"\caption{\textbf{Forward collapse: how often an adaptation answers the question it was "
         r"trained on when asked the other one.} Share of backward (input-prediction) replies that "
         r"are exactly the gold \emph{forward} answer, pooled over all "
         + str(len(agg["conditions"])) + r" backward conditions. Not a parse failure: the arm "
         r"answered the other question. The untuned model is a floor, and both merges sit on it; "
         r"every single-adapter arm is above it, highest for the arm whose extra loss term is a "
         r"KL to the clean parent's answer-token distribution. \texttt{--} marks a cell not run.}",
         r"\label{tab:forward_collapse}",
         r"\begin{tabular}{@{}l" + "r"*len(COLLAPSE_SYS) + r"@{}}", r"\toprule",
         "model & " + " & ".join(n for n, _ in COLLAPSE_SYS) + r" \\", r"\midrule"]
    for m in MODELS:
        r = by.get(m, {})
        cells = []
        for _, sy in COLLAPSE_SYS:
            v = r.get(sy, {}).get("collapse_rate")
            cells.append("--" if v is None else f"{v:.3f}")
        L.append(tex_esc(NICE[m]) + " & " + " & ".join(cells) + r" \\")
    L.append(r"\midrule")
    L.append(r"\emph{panel mean} & " + " & ".join(
        "--" if means.get(sy) is None else (r"\textbf{" + f"{means[sy]:.3f}" + "}")
        for _, sy in COLLAPSE_SYS) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)

_ct = collapse_tex()
if _ct:
    write("master_collapse.tex", _ct,
          "results/analysis/pipeline/backward_failure_modes_C_L1r_X1.json (67_backward_failure_modes.py --aggregate)",
          "Not \\input by any section yet -- prose frozen.")
else:
    print("  [collapse table] skipped: run 67_backward_failure_modes.py --aggregate first", file=sys.stderr)

# markdown twin
out.append("\n## 6. Absolute master tables — every method × every obfuscation\n")
out.append("Raw exact-match accuracy, with `%b` after each system: its accuracy as a percentage of `base`'s on the same condition. "
           "A gated cell (format-failure rate over 0.25) carries one of two marks, and the difference matters: "
           "`†` means most of its replies are unparseable — the prompt contract failing, an artefact of a template "
           "written for CodeLlama-7B — while `‡` means most of its replies are exactly the gold FORWARD answer. "
           "The second is not a broken cell: it is the arm answering the other question, which is the forward-locking "
           "result showing up as a parse failure. `--` is a cell not run.\n\n"
           "**The backward block is reported twice.** *By execution* accepts any call that returns the gold value — inversion is "
           "many-to-one, so a guess landing on a common return value scores. *By exact arguments* requires the gold call. "
           "64–69% of every system's backward successes on CodeLlama-7B are of the first kind, which is why the untuned model looks "
           "almost as good backwards as forwards (0.279 by execution, 0.086 by arguments).\n")
def md_row(m, c, bwd=False, strict=False):
    if strict:
        b=args_exact(m,"base",c); cells=[]
        for _,sy in ABS_SYS:
            if sy == "base_1shot": cells += ["--","--"]; continue
            a=args_exact(m,sy,c); cells += ["--" if a is None else f"{a:.3f}", fp(pct_of_base(a,b))]
        return cells
    ba,bf=abs_cell(m,"base",c,bwd); base_ok = ba if isinstance(ba,float) and (bf or 0)<=FMT_MAX else None
    cells=[]
    for _,sy in ABS_SYS:
        if bwd and sy == "base_1shot": cells += ["--","--"]; continue
        a,ff=abs_cell(m,sy,c,bwd)
        cr = collapse_rate(m, sy, c) if (bwd and (ff or 0) > FMT_MAX) else None
        cells += [abs_fmt(a,ff,tex=False,collapse=cr), fp(pct_of_base(a if isinstance(a,float) and (ff or 0)<=FMT_MAX else None, base_ok))]
    return cells
for m in MODELS:
    out.append(f"\n### {NICE[m]}\n")
    hdr = "| condition | " + " | ".join(f"{n} | %b" for n,_ in ABS_SYS) + " |"
    out.append(hdr); out.append("|---|" + "---:|"*(2*len(ABS_SYS)))
    for c in ABS_ROWS:
        out.append(f"| {c} | " + " | ".join(md_row(m,c)) + " |")
    out.append(f"| *backward, by execution* |" + " |"*(2*len(ABS_SYS)))
    for c in BWD_ROWS:
        if abs_cell(m,"base",c,True)[0] is None: continue
        out.append(f"| {c} | " + " | ".join(md_row(m,c,bwd=True)) + " |")
    out.append(f"| *backward, by exact arguments* |" + " |"*(2*len(ABS_SYS)))
    for c in BWD_ROWS:
        if args_exact(m,"base",c) is None: continue
        out.append(f"| {c} | " + " | ".join(md_row(m,c,strict=True)) + " |")
(ROOT/"docs/MASTER_TABLES.md").write_text("\n".join(out) + "\n")
