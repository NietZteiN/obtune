#!/bin/bash
# Keep the manifest queue moving while the master-table backfill runs (2026-09-13).
# Emits one line per submission, per failure, and a periodic status; exits when the queue is empty
# AND nothing of ours is left running, so the watch ends by itself.
#
# PARTITION POLICY. h100 and a30 carry no QOS and take the bulk; h200 is capped at obtune's agreed
# share of 2 and submit.py refuses above it, so the h200 pass is limited and its refusal is not an
# error. 34B jobs go to h200 only, at 96-128 G: a30's 24 GB cards and the default 64 G cannot hold
# 34B, which is how two of them died within a minute on 2026-09-13.
cd /work/jvl210002/migration/obtune
source scripts/env.sh
mine() { squeue -h -u "$USER" -o "%j %T %Z" | awk -v r="$PWD" '$3==r' ; }
while true; do
  left=$(ls runs/manifest/queued/*.json runs/manifest/queued_34b/*.json 2>/dev/null | wc -l)
  run=$(mine | grep -c RUNNING); pend=$(mine | grep -c PENDING)
  # a failed manifest is worth a line: it is the only signal a job died
  for f in $(ls -t runs/manifest/failed/*.json 2>/dev/null | head -3); do
    b=$(basename "$f" .json)
    case "$b" in ev_depth_*|ev_1shot_*|ev_seenfam_*|tr_L*|tr_S*)
      grep -q "^$b\$" runs/probe/.drain_seen 2>/dev/null || { echo "FAILED manifest: $b"; echo "$b" >> runs/probe/.drain_seen; } ;;
    esac
  done
  if [ "$left" -eq 0 ] && [ "$run" -eq 0 ] && [ "$pend" -eq 0 ]; then
    echo "queue drained: nothing queued, running or pending"; break
  fi
  # Hold more work in SLURM'"'"'s queue than in ours. h100 and a30 are uncapped, so a pending job there
  # costs nothing and buys a better backfill position; only h200 is share-limited, and submit.py
  # refuses past the share on its own. 8 was too tight while another user held six h100 jobs.
  if [ "$((run+pend))" -lt 14 ] && [ "$left" -gt 0 ]; then
    # 34B needs 128 G of host memory (the earlier 34B runs used it); everything else gets 64-96 G,
    # because over-requesting is not free -- 128 G on a memory-starved h200 once scheduled a job a
    # day out. So the h200 pass asks for 128 G only while a 34B manifest is next in line.
    h200mem=96G
    next34b=$(ls runs/manifest/queued/*.json 2>/dev/null | xargs -r -n1 basename 2>/dev/null | grep -c 34b)
    only34b=$(ls runs/manifest/queued/*.json 2>/dev/null | wc -l)
    [ "$next34b" -gt 0 ] && [ "$next34b" -eq "$only34b" ] && h200mem=128G
    # a30 cards are 23.5 GB. 13B bf16 needs ~26 GB and OOM'd two minutes in on 2026-09-13; 12B and
    # 15B do not fit either. Only the 7-8B models go there, one named manifest at a time, because
    # `--queued` drains by priority and cannot filter. h100 and h200 take anything.
    for spec in "h100 3 64G" "h200 1 $h200mem"; do
      set -- $spec
      out=$(timeout 300 python scripts/slurm/submit.py --queued --partition "$1" --limit "$2" --mem "$3" 2>&1 | grep -E "^submitted|FAILED|REFUSING" | grep -v REFUSING)
      [ -n "$out" ] && echo "$out" | sed "s/^/[$1] /"
    done
    # a30 takes CodeLlama-7B TRAININGS ONLY. 23.5 GB holds 6.7B and nothing above it: every 8B model
    # has OOM'd there -- Granite-3.1-8B and Llama-3.1-8B on S3, CodeGemma (8.5B, 256k vocab) on L2,
    # CodeLlama-13B on L1r. The bound was raised twice on partial evidence before landing here.
    # a30 also cannot SERVE these models: vLLM on an 8.5B model leaves 0.92 GiB for
    # the KV cache against the 3.5 GiB an 8192-token context needs, and the engine refuses to start
    # (ev_1shot_codegemma-7b, 2026-09-13). Training fits because there is no KV cache to reserve.
    # 34B IS h200-ONLY, for serving as well as training: its 68 GB of bf16 weights leave no room for a
    # KV cache on an 80 GB h100 card (ev_depth_codellama-34b, 2026-09-13), and a30 is far too small.
    # Its manifests are parked in queued_34b/, which the --queued passes above cannot see, and are
    # submitted by name here with the memory 34B needs.
    # Two per tick, matching obtune's h200 share; submit.py refuses past it, so this cannot overrun.
    for j in $(ls runs/manifest/queued_34b/*.json 2>/dev/null | head -2); do
      # A manifest stays in queued_34b until its job STARTS, so without this the next tick submits it
      # again -- two 2-hour 34B jobs for one piece of work (tr_S4_codellama-34b, 2026-09-13). The
      # --queued passes are idempotent on live job names already; this by-name path was not.
      squeue -h -u "$USER" -o "%j" | grep -qx "$(basename "$j" .json)" && continue
      out=$(timeout 300 python scripts/slurm/submit.py --job "$j" --partition h200 --mem 128G 2>&1 | grep -E "^submitted|FAILED")
      [ -n "$out" ] && echo "$out" | sed "s/^/[h200-34b] /"
    done
    for j in $(ls runs/manifest/queued/tr_*.json 2>/dev/null | grep -E "codellama-7b" | head -2); do
      out=$(timeout 300 python scripts/slurm/submit.py --job "$j" --partition a30 --mem 64G 2>&1 | grep -E "^submitted|FAILED")
      [ -n "$out" ] && echo "$out" | sed "s/^/[a30] /"
    done
  fi
  # Advance the routing/merging track too: training a specialist leaves checkpoint-*/ and final/, not
  # best/, and merge_adapters.py defaults to best. This checkpoint-selects whatever is ready and merges
  # any model whose five specialists are selected -- readiness-driven, so it is safe to call every tick.
  # Only real submissions are events; the script's own "submitted 0 ... and 0 ..." summary is not.
  adv=$(timeout 600 python scripts/merge/build_ready_merges.py --submit 2>&1 | grep -E "^ +submitted [0-9]+ +(ckb_|mg_)")
  [ -n "$adv" ] && echo "$adv" | sed "s/^ */[merge-track] /"
  # As soon as a model's three merges exist, queue its merge evaluation. Without this the merges sit
  # built-but-unmeasured until someone notices, which is the same stall the checkpoint-select step had.
  for m in codellama-13b gemma3-12b codegemma-7b codellama-34b; do
    built=$(ls -d runs/adapters/$m/python/merge_*_r32_s17/adapter_model.safetensors 2>/dev/null | wc -l)
    cells=$(ls results/cells/merge_panel/$m/python 2>/dev/null | wc -l)
    # 34B is h200-only for serving, so its manifests go to the parked queue the h200 pass reads.
    qdir=runs/manifest/queued; case "$m" in *34b*) qdir=runs/manifest/queued_34b ;; esac
    mf=$qdir/ev_merge_$m.json
    if [ "$built" -ge 3 ] && [ "$cells" -eq 0 ] && [ ! -f "$mf" ] \
       && ! ls runs/manifest/{running,done}/ev_merge_$m.json >/dev/null 2>&1 \
       && ! squeue -h -u "$USER" -o "%j" | grep -qx "ev_merge_$m"; then
      printf '{"job_id":"ev_merge_%s","kind":"eval","argv":["-m","obtune.eval_vllm","--config","eval/merge_panel.yaml","--model","%s","--language","python"],"raw":false,"est_gpu_h":0.6,"priority":115,"meta":{"note":"master table: the merge column, queued automatically once the three merges were built"}}\n' "$m" "$m" > "$mf"
      echo "[merge-track] queued ev_merge_$m (merges are built)"
    fi
  done
  # Router gates: readiness-driven like the merges. A gate needs all EIGHT experts with best/
  # (L0..S2 plus S3 and S4); until S3/S4 land the config cannot run, so this checks rather than chains.
  for m in codellama-13b llama31-8b starcoder2-15b gemma3-12b codegemma-7b granite31-8b codellama-34b; do
    have=0
    for c in L0 L1b L1r L2 S1 S2 S3 S4; do
      [ -f "runs/adapters/$m/python/${c}_r32_s17/best/adapter_model.safetensors" ] && have=$((have+1))
    done
    # train_mole appends the seed to run_tag: the 7B gate lives in routerlora_codellama7b_s17/.
    tag="routerlora_$(echo $m | tr -d '-')_s17"
    # 34B gate training needs h200: the base model is ~68 GB before the eight-expert bank.
    qdir=runs/manifest/queued; case "$m" in *34b*) qdir=runs/manifest/queued_34b ;; esac
    mf=$qdir/tr_gate_$m.json
    if [ "$have" -eq 8 ] && [ ! -f "runs/mole/$m/python/$tag/gate.pt" ] && [ ! -f "$mf" ] \
       && ! ls runs/manifest/{running,done}/tr_gate_$m.json >/dev/null 2>&1 \
       && ! squeue -h -u "$USER" -o "%j" | grep -qx "tr_gate_$m"; then
      printf '{"job_id":"tr_gate_%s","kind":"train","argv":["-m","obtune.mole.train_mole","--config","mole/routerlora_%s.yaml"],"raw":false,"est_gpu_h":3.0,"priority":280,"meta":{"note":"master table: the mixture arm -- router gate over the eight experts, queued automatically once all eight existed"}}\n' "$m" "$m" > "$mf"
      echo "[mixture] queued tr_gate_$m (8/8 experts ready)"
    fi
  done
  # Mixture evaluation, once a gate exists. Runs through obtune.mole.eval_mole -- vLLM has no mixture
  # path and refuses these arches (the guard that cost a day on 2026-09-12/13).
  for m in codellama-13b llama31-8b starcoder2-15b gemma3-12b codegemma-7b granite31-8b codellama-34b; do
    tag="routerlora_$(echo $m | tr -d '-')_s17"
    cells=$(ls -d results/cells/mole_generic/$m/python/mole_* 2>/dev/null | wc -l)
    # 34B is h200-only for serving, so its manifests go to the parked queue the h200 pass reads.
    qdir=runs/manifest/queued; case "$m" in *34b*) qdir=runs/manifest/queued_34b ;; esac
    mf=$qdir/ev_mole_$m.json
    if [ -f "runs/mole/$m/python/$tag/gate.pt" ] && [ "$cells" -eq 0 ] && [ ! -f "$mf" ] \
       && ! ls runs/manifest/{running,done}/ev_mole_$m.json >/dev/null 2>&1 \
       && ! squeue -h -u "$USER" -o "%j" | grep -qx "ev_mole_$m"; then
      printf '{"job_id":"ev_mole_%s","kind":"eval","argv":["-m","obtune.mole.eval_mole","--config","eval/mole_panel_%s.yaml","--model","%s","--language","python"],"raw":false,"est_gpu_h":1.5,"priority":125,"meta":{"note":"master table: the mixture column, queued automatically once the router gate existed"}}\n' "$m" "$m" "$m" > "$mf"
      echo "[mixture] queued ev_mole_$m (gate is trained)"
    fi
  done
  echo "[status] queued=$left running=$run pending=$pend"
  sleep 240
done
