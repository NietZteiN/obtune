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
        "llama31-8b-base":"Llama-3.1-8B (base)", "qwen25c-1.5b":"Qwen2.5-Coder-1.5B (pilot)"}
PARAMS_B = {"codellama-7b":6.7,"codellama-13b":13.0,"codellama-34b":33.7,"llama31-8b":8.0,"starcoder2-15b":15.5,
            "gemma3-12b":12.2,"codegemma-7b":8.5,"granite31-8b":8.2,"llama31-8b-base":8.0}  # nominal, from the model cards
LADDER = ["L0","L1b","L1r","L2","S1","S2","X1"]
SEEN_STACKS = ["C_L1b_S1","C_L1r_S1","C_S1_L1r","C_L2_S4","C_L1r_S3","C_S4_S3"]
DEPTH_STACKS = ["C3_L1r_S3_S4","C3_S1_S3_S4","C3_L1r_S1_S4","C4_L1r_S1_S3_S4"]
UNSEEN_STACKS = ["C_L1r_X1","C_X1_S1","C_S2_X1"]
HALF_STACKS = ["C_L1r_X1m","C_S1_X1s"]
D3_STACKS = ["C3_L1r_S1_X1"]
# Names match the main table and Appendix A (2026-09-17): "anchored" -> KL.
INTERV = [("ICL","base_1shot"),("clean LoRA","tuned_L0"),("breadth","mono_all"),("KL","cons_lam3"),("family","tuned_X1")]
PHASES = {"ladder":["panel_core"],"seen":["composite_generic"],"depth":["composite_depth","composite_generic"],
          "unseen":["f2_divergence"],"half":["f2_divergence"],"d3":["f2_divergence"]}
KIND = {}
for c in LADDER: KIND[c]="ladder"
# S3/S4 are single transforms too. The eight-model panel never evaluates them as standalone
# conditions (they exist only as experts and inside stacks), but the Qwen pilot did, and
# abs_cell resolves a phase through KIND, so they need an entry or the Qwen table cannot read them.
for c in ["S3","S4"]: KIND[c]="ladder"
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
# Citations for the panel table (2026-09-17, user: "add citations to model panel"). Keys are in
# paper/router_merger/references.bib; CodeLlama and StarCoder2 reuse entries that were already there,
# the other three were added with arXiv ids verified against arxiv.org. Granite has NO arXiv paper for
# the 3.x instruct family -- the arXiv Granite papers are Code/Vision/Guardian/Embedding/Speech -- so
# it is cited by its release page rather than with an invented identifier.
CITE = {"codellama-7b":"code_llama", "codellama-13b":"code_llama", "codellama-34b":"code_llama",
        "llama31-8b":"llama3herd", "starcoder2-15b":"lozhkov2024starcoder2stackv2",
        "gemma3-12b":"gemma3", "codegemma-7b":"codegemma", "granite31-8b":"granite31"}

def cite(k):
    c = CITE.get(k)
    return f"~\\cite{{{c}}}" if c else ""

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
       "KL":r"KL (\texttt{cons\_lam3})","family":r"family (\texttt{tuned\_X1})"}
SYS2 = {"ICL":(r"ICL",r"\texttt{base\_1shot}"),"clean LoRA":(r"clean LoRA",r"\texttt{tuned\_L0}"),"breadth":(r"breadth",r"\texttt{mono\_all}"),
        "KL":(r"KL",r"\texttt{cons\_lam3}"),"family":(r"family",r"\texttt{tuned\_X1}")}
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
     r"the number gated as \emph{fmt}). Systems: ICL = \texttt{base\_1shot}, clean LoRA = \texttt{tuned\_L0}, breadth = \texttt{mono\_all}, KL = \texttt{cons\_lam3}, family = \texttt{tuned\_X1}. "
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
# Citations widened the Model column by ~11.5 pt past the text block. 2 pt padding took 5.6 pt of
# that; the checkpoint column is the other half, and \tiny on the hf_id alone keeps the model names
# and the citations at \scriptsize where they are read.
L = [r"\begin{table*}[ht]", r"\centering\scriptsize\setlength{\tabcolsep}{2pt}",
     r"\caption{\textbf{The model panel.} Four lineages, code-specialised and general instruct models, 7B to 34B. \emph{Chat template}: "
     r"\emph{system} accepts a system role; \emph{merged} folds the system text into the user turn; \emph{plain} has no template and is used "
     r"for the one-shot baseline only. Parameter counts are nominal. Every adapter is a LoRA with the same rank and target modules on every model.}",
     r"\label{tab:models}", r"\begin{tabular}{@{}llllrrrl@{}}", r"\toprule",
     r"\textbf{Model} & \textbf{Checkpoint} & \textbf{Lineage} & \textbf{Type} & \textbf{Params (B)} & \textbf{Layers} & \textbf{Hidden} & \textbf{Chat template} \\", r"\midrule"]
for k in MODELS + ["llama31-8b-base"]:
    v = mm[k]
    # llama31-8b-base is the pretrained twin of llama31-8b and shares its citation.
    L.append(f"{NICE[k]}{cite('llama31-8b' if k == 'llama31-8b-base' else k)} & " + r"\texttt{\tiny " + tex_esc(v['hf_id']) + "}" + f" & {origin(k,v)} & {v.get('family')} & {PARAMS_B[k]} & {v.get('n_layers')} & {v.get('hidden_size')} & {v.get('render_mode') or 'system'} " + r"\\")
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
L.append(r"Coverage per condition & Table~\ref{tab:taxonomy} and Appendix~\ref{app:absmaster}; structural transforms decline some programs by design, the unseen family needs $\geq 3$ encodable sites \\")
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
# `family` (tuned_X1) REMOVED from the table 2026-09-14 at the user's request. It is trained on X1,
# the held-out family's sibling, so on the rows that matter most -- anything containing the unseen
# family -- it is the one arm for which that family is not unseen, and it wins those rows by having
# been trained on them. The same reason it was dropped from 69_stack_leaderboard.py and
# 65_backward_stacks.py earlier today. Its cells are untouched and still in docs/MASTER_TABLES.md.
# Column names match the main results table (2026-09-17): "anchored" -> KL, "mixture" -> router.
ABS_SYS = [("base","base"),("ICL","base_1shot"),("clean LoRA","tuned_L0"),("breadth","mono_all"),("KL","cons_lam3"),
           ("router","mole_router"),("merge","merge_dare_ties")]
ABS_PH = {"base":None, "base_1shot":["basecheck_1shot"], "tuned_L0":None, "mono_all":None, "cons_lam3":None, "tuned_X1":None,
          "mole_router":["mole_generic"], "merge_dare_ties":["merge_panel","rq2_generic","composite_generic","f2_divergence"]}
ABS_ROWS = LADDER + SEEN_STACKS + DEPTH_STACKS + UNSEEN_STACKS + HALF_STACKS + D3_STACKS

# THE QWEN PILOT (2026-09-14, user request: "add another table like master table but with Qwen
# result below table 5"). qwen25c-1.5b is the model the project piloted on before the eight-model
# panel existed, so its cells sit in the pilot-era phases (`baselines`, `align_lam_sweep`, `main`)
# rather than `panel_core`/`composite_generic`, and it has a DIFFERENT condition set: S3 and S4 as
# standalone transforms, which the panel never ran, and no X1, no depth-3/4 stacks, no
# unseen-containing stacks, because those were designed after it. Three of the eight methods were
# never built for it (ICL, anchored, family) and render `--`.
# H1 IS DELIBERATELY ABSENT from QWEN_ROWS. Qwen has H1 cells on disk from the pilot; CLAUDE.md
# 3.2 rule 3 forbids any further read, and this table would be a read.
# QWEN REMOVED 2026-09-15 at the user's instruction ("don't run Qwen ... we're not allowed to").
# The pilot model is out of scope for this project: it must not be run, and it must not appear in
# the paper. Left as an empty list rather than deleting the mechanism, because ABS_ROWS_BY_MODEL /
# ABS_PH_BY_MODEL below are generic and may serve another off-panel model later.
ABS_EXTRA_MODELS: list[str] = []
QWEN_ROWS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "S3", "S4"] + SEEN_STACKS
assert "H1" not in QWEN_ROWS, "H1 is quarantined (CLAUDE.md 3.2)"
ABS_ROWS_BY_MODEL = {"qwen25c-1.5b": QWEN_ROWS}
_QWEN_BASE_PH = ["baselines", "align_lam_sweep", "baselines_gridA", "main", "final"]
ABS_PH_BY_MODEL = {"qwen25c-1.5b": {
    "base": _QWEN_BASE_PH, "tuned_L0": _QWEN_BASE_PH, "base_1shot": ["basecheck_1shot"],
    "mono_all": ["main"], "cons_lam3": ["main"], "tuned_X1": ["main"],
    "mole_router": ["main"], "merge_dare_ties": ["main"]}}

# AVERAGE ROWS (user, 2026-09-14: "averages for single obfuscation, held out, and all of the depths
# each one so I can see those at a glance"). Depth and seen/unseen are crossed, because a depth-3
# stack that contains the held-out family is a different question from one that does not -- that
# distinction is the whole of RQ1 -- so they are separate rows rather than one "depth 3" row.
AVG_GROUPS = [
    ("single obfuscation",      ["L1b", "L1r", "L2", "S1", "S2", "S3", "S4"]),
    ("held-out family",         ["X1"]),
    ("depth 2, all seen",       SEEN_STACKS),
    ("depth 3, all seen",       ["C3_L1r_S3_S4", "C3_S1_S3_S4", "C3_L1r_S1_S4"]),
    ("depth 4, all seen",       ["C4_L1r_S1_S3_S4"]),
    ("depth 2, unseen inside",  UNSEEN_STACKS + HALF_STACKS),
    ("depth 3, unseen inside",  D3_STACKS),
]

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
        over = ABS_PH_BY_MODEL.get(m, {})
        ph = over.get(sysn) or ABS_PH.get(sysn) or PHASES[KIND[c]]
        a, ff = acc(ph, m, sysn, c)
        if a is None and ABS_PH.get(sysn) is None: a, ff = acc(B_PH, m, sysn, c)
    return a, ff

def colourise(a, b, txt):
    """Green when this system is ABOVE `base` on this condition, red when below (user, 2026-09-14).

    Applied to the accuracy only, never to the `%b` column beside it: `%b` already IS the comparison
    to base, so colouring both would say the same thing twice. `base` itself is the reference and is
    never coloured, and neither is a cell whose reference is missing or format-gated -- an
    uncoloured number means "no comparison available", which is different from "equal".
    xcolor and colortbl are both already in the paper's preamble.
    """
    if not isinstance(a, float) or not isinstance(b, float):
        return txt
    # Only colour a difference that is VISIBLE at the three decimals printed. Without this, a mean
    # of 0.2984 against a base of 0.2985 printed as "0.298" beside "0.298" and 100 %, in red --
    # a reader would read that as a bug in the table rather than a rounding boundary.
    if abs(a - b) < 5e-4:
        return txt
    if a > b:
        return r"\textcolor{green!55!black}{" + txt + "}"
    if a < b:
        return r"\textcolor{red!70!black}{" + txt + "}"
    return txt


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
    """ONE full-width float per model, every cell `output / input` (user, 2026-09-14: "I wanted like
    output/input so it can fit in one table").

    The previous layout was two floats per model, forward then backward, each with an accuracy AND
    a %-of-base column per arm. Folding the two directions into one cell and dropping %-of-base --
    which the colour already encodes -- takes a model from 2 x 15 columns x ~32 rows to 8 columns x
    ~33 rows, which fits one page at \footnotesize. The backward half of a cell is `--` where that
    direction was not run (the ICL arm has no backward read; the pilot's stacks beyond depth 2 do
    not exist). The forward label `tab:master_abs_<tag>` is kept; the `_bwd` labels are gone, and
    the two prose references to them are rewritten in sections/master.tex.
    """
    SEP = r"\,/\,"
    rows_for_m = ABS_ROWS_BY_MODEL.get(m, ABS_ROWS)
    tag = m.replace("-","").replace(".","")
    ncol = 1 + len(ABS_SYS)

    def half(sy, c, bwd):
        if bwd and sy == "base_1shot":
            return "--"
        a, ff = abs_cell(m, sy, c, bwd)
        if a is None:
            return "--"
        ba, bf = abs_cell(m, "base", c, bwd)
        base_ok = ba if isinstance(ba, float) and (bf or 0) <= FMT_MAX else None
        cr = collapse_rate(m, sy, c) if (bwd and (ff or 0) > FMT_MAX) else None
        txt = abs_fmt(a, ff, collapse=cr)
        if (ff or 0) > FMT_MAX:
            # A FORMAT-GATED CELL IS RED (user, 2026-09-15: "for star format error stuff also put
            # it as red"). 954 of the 8,852 cells on disk are gated, and they were the only numbers
            # in the table with no colour at all -- so the cell a reader should trust least looked
            # the same as one with no comparison available. It keeps its dagger, and that marker is
            # what separates the two meanings of red: RED + MARKER is unreliable (over a quarter of
            # its replies failed the output contract, so the accuracy underneath is not a fair
            # reading), RED ALONE is a sound number that is simply below base. Applied to `base`
            # too, unlike the below-base colour: base is the comparison reference, but a gated base
            # is not a usable reference -- StarCoder2 forward is the extreme, 1.000 format failure.
            return r"\textcolor{red!70!black}{" + txt + "}"
        a_ok = a if isinstance(a, float) and (ff or 0) <= FMT_MAX else None
        return txt if sy == "base" else colourise(a_ok, base_ok, txt)

    def row(c):
        return [half(sy, c, False) + SEP + half(sy, c, True) for _, sy in ABS_SYS]

    def avg_row(conds):
        """Mean over the group's readable cells, per direction. A missing or format-gated member is
        dropped rather than voiding the mean, and a superscript gives the count used when short."""
        use = [c for c in conds if c in rows_for_m]
        def mean_of(sy, bwd):
            vals = []
            for c in use:
                a, ff = abs_cell(m, sy, c, bwd)
                if isinstance(a, float) and (ff or 0) <= FMT_MAX:
                    vals.append(a)
            return (sum(vals)/len(vals), len(vals)) if vals else (None, 0)
        ref = {bwd: mean_of("base", bwd)[0] for bwd in (False, True)}
        out = []
        for _, sy in ABS_SYS:
            halves = []
            for bwd in (False, True):
                if bwd and sy == "base_1shot":
                    halves.append("--"); continue
                v, n = mean_of(sy, bwd)
                if v is None:
                    halves.append("--"); continue
                txt = f"{v:.3f}" + ("" if n == len(use) else r"$^{" + str(n) + "}$")
                halves.append(txt if sy == "base" else colourise(v, ref[bwd], txt))
            out.append(halves[0] + SEP + halves[1])
        return out

    def avg_block():
        out = []
        for label, conds in AVG_GROUPS:
            if not [c for c in conds if c in rows_for_m]:
                continue
            out.append(r"\textbf{" + label + "} & " + " & ".join(avg_row(conds)) + r" \\")
        return ([r"\cmidrule(l{2pt}r{2pt}){1-" + str(ncol) + "}"] + out) if out else []

    caption = (r"\textbf{Every method against every obfuscation, " + NICE[m] + r".} "
               r"Each cell is \emph{output prediction}\,/\,\emph{input prediction}: raw exact-match accuracy on the "
               r"forward task (predict the return value of the code as shown) and, after the slash, on the backward "
               r"task (produce a call that returns the shown value), on the held-out programs of that condition. "
               r"\emph{base} is the untuned model; \emph{ICL} its one-shot prompt; \emph{clean LoRA} is tuned on "
               r"unobfuscated code; \emph{breadth} on all six training conditions pooled; \emph{KL} adds a "
               r"KL-consistency term to a frozen clean-code teacher (Eq.~\ref{eq:kl}); \emph{router} is the "
               r"learned-gate mixture of per-transform "
               r"specialists; \emph{merge} is the DARE-TIES merge of them. "
               r"\textbf{Colour}: an accuracy \textcolor{green!55!black}{above} or \textcolor{red!70!black}{below} "
               r"\texttt{base} in the same direction on the same condition; \texttt{base} is the reference, and an "
               r"uncoloured number means no comparison was available rather than a tie. A \textcolor{red!70!black}{red "
               r"number carrying $\dagger$ or $\ddagger$} is red for the other reason --- its format-failure rate is "
               r"above 0.25, so the accuracy beneath it is not a fair reading of the arm --- and those cells are "
               r"excluded from the bold means. \textbf{Bold rows} are means "
               r"over the group named, equally weighted per condition; a superscript gives the number of readable "
               r"cells averaged when it is short of the group. The family adapter (\texttt{tuned\_X1}) is deliberately "
               r"not a column: it is trained on the held-out family's sibling, so on exactly the rows that matter "
               r"most it is the one arm for which that family is not held out; the \textbf{held-out family} row "
               r"names a group of conditions, not an arm. "
               r"\textbf{Backward is graded by execution}: any call returning the gold value is correct, because "
               r"inversion is many-to-one. $\dagger$: format-failure rate above 0.25, mostly replies that do not "
               r"meet the output contract. $\ddagger$: above 0.25 backward, but most replies are exactly the gold "
               r"\emph{forward} answer --- the arm answered the other question, which is a result rather than a "
               r"broken template. "
               + (r"\textbf{This model is the pilot}: it predates X1, the depth-3/4 stacks and the "
                  r"unseen-containing stacks, and the in-context, KL and family arms were never built for it, "
                  r"so those rows and columns are absent rather than empty; it does carry \texttt{S3}/\texttt{S4} as "
                  r"standalone transforms, which the panel models do not. " if m in ABS_EXTRA_MODELS else "")
               + r"`--': not run.")

    body = [r"\texttt{" + tex_esc(c) + "} & " + " & ".join(row(c)) + r" \\" for c in rows_for_m] + avg_block()
    return "\n".join(
        [r"\begin{table*}[p]",
         r"\centering\footnotesize\setlength{\tabcolsep}{2pt}\renewcommand{\arraystretch}{0.95}",
         r"\caption{" + caption + "}",
         r"\label{tab:master_abs_" + tag + "}",
         r"\begin{tabular}{@{}l" + "c"*len(ABS_SYS) + "@{}}", r"\toprule",
         r"\textbf{Condition} & " + " & ".join(r"\textbf{" + n + "}" for n, _ in ABS_SYS) + r" \\",
         " & " + " & ".join(r"{\scriptsize out\,/\,in}" for _ in ABS_SYS) + r" \\", r"\midrule"]
        + body + [r"\bottomrule", r"\end{tabular}", r"\end{table*}"])


for m in MODELS + ABS_EXTRA_MODELS:
    write(f"master_abs_{m.replace('-','').replace('.','')}.tex", abs_table(m),
          "results/cells/* for " + m + " (raw accuracies, and % of base)")

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
                ("KL","cons_lam3"),("router","mole_router")]

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

# ---------------- 8. THE MAIN RESULTS TABLE ---------------------------------------------------
# One panel-wide table for the BODY (2026-09-15, user: "one main table of results, failing methods
# as baseline"). The nine per-model tables are the appendix; this is what a reader sees first.
#
# Three blocks, chosen because they are the three regimes where the arms behave differently:
#   SEEN STACKS      composed transforms the specialists were trained on -- everything works here
#   UNSEEN FAMILY    X1 and the stacks containing it -- where breadth collapses
#   BACKWARD         input prediction, execution-graded -- where single adapters lock
# Every number is the equally-weighted mean over that block's conditions, computed by the SAME
# abs_cell path as the per-model tables' bold rows, so the summary and the appendix cannot drift.
#
# Bolding the best non-base arm per block per model is the point of the table: on the seen block the
# bold lands on anchored/mixture, on the backward block it lands on the merge. That pattern IS the
# paper's claim, and it is visible without reading a number.
MAIN_BLOCKS = [("seen stacks", SEEN_STACKS + DEPTH_STACKS),
               ("unseen family", ["X1"] + UNSEEN_STACKS + HALF_STACKS + D3_STACKS),
               ("backward (input pred.)", None)]   # None = every backward condition available
MAIN_SYS = [("base","base"),("clean","tuned_L0"),("breadth","mono_all"),
            ("KL","cons_lam3"),("router","mole_router"),("merge","merge_dare_ties")]

def _block_mean(m, sy, conds, bwd):
    """Mean over readable cells; None when the arm has none. Gated cells are dropped, exactly as in
    the per-model tables -- an arm whose whole block is gated reads `--`, not a fabricated number."""
    use = conds if conds is not None else BWD_ROWS
    vals = []
    for c in use:
        a, ff = abs_cell(m, sy, c, bwd)
        if isinstance(a, float) and (ff or 0) <= FMT_MAX:
            vals.append(a)
    return (sum(vals)/len(vals), len(vals)) if vals else (None, 0)

# Short row labels: the full names cost 39 pt of width across eight rows in a table that was already
# at the margin, and the lineage is the only part a reader needs here.
SHORT = {"codellama-7b":"CodeLlama-7B","codellama-13b":"CodeLlama-13B","codellama-34b":"CodeLlama-34B",
         "llama31-8b":"Llama-3.1-8B","starcoder2-15b":"StarCoder2-15B","gemma3-12b":"Gemma-3-12B",
         "codegemma-7b":"CodeGemma-7B","granite31-8b":"Granite-3.1-8B"}

def main_table():
    # 19 columns at \footnotesize ran 124 pt past the two-column text block. \scriptsize with 2 pt
    # padding brings it inside; the alternative -- dropping the per-block `base` column -- would cost
    # the reader the level each block's colours are relative to, which is worth more than the font.
    L = [r"\begin{table*}[t]", r"\centering\scriptsize\setlength{\tabcolsep}{2pt}",
         r"\caption{\textbf{Every adaptation on every model, in the three regimes that separate them.} "
         r"Mean exact-match accuracy over the conditions in each block, equally weighted; the same "
         r"numbers as the bold rows of the per-model tables in Appendix~\ref{app:absmaster}. "
         r"\emph{seen stacks}: depth-2/3/4 compositions of the seen transforms; seven of its ten "
         r"conditions include \texttt{S3} or \texttt{S4}, which the mixture has experts for and \emph{breadth} "
         r"and \emph{merge} do not. "
         r"--- no arm was trained on it. \emph{backward}: input prediction, graded by execution. "
         r"\emph{base} is the untuned model, \emph{clean} a LoRA tuned on unobfuscated code, "
         r"\emph{breadth} one LoRA tuned on all six training conditions at once, \emph{KL} the "
         r"KL-consistency objective, \emph{router} a learned-gate mixture of eight per-condition "
         r"specialists, \emph{merge} the DARE-TIES merge of the six that breadth pools. \emph{breadth} and "
         r"\emph{merge} are exactly data-matched; \emph{mix} carries two further experts "
         r"(\texttt{S3}, \texttt{S4}) that neither is trained on. "
         r"\textbf{Bold} is the best non-base arm in that block; "
         r"\textcolor{red!70!black}{red} is below \texttt{base}. "
         r"`--': no cell in the block survived the 0.25 format gate. "
         r"\textbf{Read the bold across the blocks}: on seen stacks it falls on the single-adapter "
         r"arms, and on the two out-of-distribution blocks it moves to the arms composed from "
         r"per-transform specialists.}",
         r"\label{tab:main}",
         r"\resizebox{\textwidth}{!}{%",
         r"\begin{tabular}{@{}l" + ("r"*len(MAIN_SYS) + "@{\\ }")*len(MAIN_BLOCKS) + "@{}}",
         r"\toprule"]
    L.append(" & " + " & ".join(r"\multicolumn{" + str(len(MAIN_SYS)) + r"}{c}{\textbf{" + b + "}}"
                                for b, _ in MAIN_BLOCKS) + r" \\")
    L.append(r"\cmidrule(lr){2-7}\cmidrule(lr){8-13}\cmidrule(lr){14-19}")
    L.append(r"\textbf{model} & " + " & ".join(" & ".join(n for n, _ in MAIN_SYS) for _ in MAIN_BLOCKS) + r" \\")
    L.append(r"\midrule")
    for m in MODELS:
        cells = []
        for bname, conds in MAIN_BLOCKS:
            bwd = conds is None
            vals = {sy: _block_mean(m, sy, conds, bwd)[0] for _, sy in MAIN_SYS}
            ref = vals["base"]
            cand = {sy: v for sy, v in vals.items() if sy != "base" and v is not None}
            best = max(cand, key=cand.get) if cand else None
            for _, sy in MAIN_SYS:
                v = vals[sy]
                if v is None:
                    cells.append("--"); continue
                t = f"{v:.3f}"
                if sy != "base" and isinstance(ref, float) and v < ref - 5e-4:
                    t = r"\textcolor{red!70!black}{" + t + "}"
                if sy == best:
                    t = r"\textbf{" + t + "}"
                cells.append(t)
        L.append(tex_esc(SHORT.get(m, NICE[m])) + " & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}}", r"\end{table*}"]
    return "\n".join(L)

write("main_results.tex", main_table(), "results/cells/* (block means, same path as the per-model tables)")
