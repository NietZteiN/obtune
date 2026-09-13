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
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT/"src"))
from obtune.config import load_config
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
        p = CELLS/ph/m/"python"/f"{s}__{c}"/"cell_meta.json"
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
def bwd(m, s, conds): return pooled(["inverse_generic"], m, s, conds) if KIND[conds[0]]=="ladder" else None
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
    for label, conds in [(c,[c]) for c in LADDER]:
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
           "graded by execution; no adapter is trained on it, and it is run on the ladder only. Each system shows three numbers: "
           "**acc** (raw accuracy), **Δ** (points against the untuned model on the same condition), and **%** (accuracy as a percentage "
           "of the untuned model's clean-code accuracy in the same direction — how much of the original accuracy the system brings "
           "back; the untuned model on clean code is 100 by definition, on obfuscated code it shows what the obfuscation removed, "
           "above 100 means more than restored). In-context learning has no backward run and no X1/stack run. **`fmt`** marks a "
           "cell whose format-failure rate exceeds 0.25: its responses are mostly unparseable, so it measures the prompt contract, "
           "not the task, and is excluded from every mean. The backward and in-context templates were written for CodeLlama-7B; "
           "they pass the gate on nearly every cell there and fail it on most cells of the other panel models.\n")
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
        cells = [r["label"], fa(r["base"][0]), fp(r["base"][1])]
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
             r"backward (input prediction, ladder only). Per system: \emph{acc} raw accuracy; $\Delta$ points against the untuned model on the "
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
