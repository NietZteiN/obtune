#!/bin/bash
# Compile a paper directory's fse27.tex to PDF inside a TeXLive container.
#
#   bash runs/probe/build_paper.sh [dir]     dir defaults to router_merger
#
# THE DEFAULT CHANGED 2026-09-14, and the old one was a trap. It was `paper_latex`, which is the
# PRE-RESTRUCTURE copy: it still carries sections/rq4.tex, which was deleted when the paper went to
# three RQs, and it has neither sections/rqs.tex nor sections/master.tex, which the current paper
# does. Meanwhile scripts/analysis/59_master_tables.py writes its tables into paper/router_merger/
# and every section edited since 2026-09-13 is there. So running this script with no argument
# rebuilt a stale paper from stale sections, reported a page count for it, and left the real
# paper's PDF and .log untouched -- which is exactly how it was used today, three times, before
# anyone noticed the log timestamp never moved. The directory being built is now printed.
# There is no LaTeX toolchain on juno; singularity is the only working container runtime
# (podman/docker cannot set up a user namespace here). Cache goes to /scratch, which has room.
set -eu
cd /work/jvl210002/migration/obtune
export SINGULARITY_CACHEDIR=/scratch/juno/$USER/singularity
export APPTAINER_CACHEDIR=$SINGULARITY_CACHEDIR
# /work is mounted nodev and refuses the xattr calls the OCI unpack makes; /scratch does not.
export SINGULARITY_TMPDIR=/scratch/juno/$USER/singularity/tmp
export APPTAINER_TMPDIR=$SINGULARITY_TMPDIR
mkdir -p "$SINGULARITY_TMPDIR"
IMG=$SINGULARITY_CACHEDIR/texlive.sif
[ -f "$IMG" ] || singularity pull "$IMG" docker://texlive/texlive:latest
# Tables are generated from the cells and INLINED into the .tex (the user asked for them built in
# rather than \input from tables/). Refresh the inlined copies before every build so a stale table
# cannot survive a regeneration; the step is idempotent and a no-op when nothing changed.
PAPER_DIR="${1:-router_merger}"
echo "# building paper/$PAPER_DIR"
if [ -d "paper/$PAPER_DIR/tables" ]; then
  python scripts/paper/inline_tables.py "paper/$PAPER_DIR" >/dev/null || true
fi
cd "paper/$PAPER_DIR"
singularity exec -B "$PWD:$PWD" --pwd "$PWD" "$IMG" \
  latexmk -pdf -interaction=nonstopmode -halt-on-error fse27.tex
