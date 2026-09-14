#!/bin/bash
# Compile paper/paper_latex/fse27.tex to PDF inside a TeXLive container.
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
if [ -d "paper/${1:-paper_latex}/tables" ]; then
  python scripts/paper/inline_tables.py "paper/${1:-paper_latex}" >/dev/null || true
fi
cd "paper/${1:-paper_latex}"
singularity exec -B "$PWD:$PWD" --pwd "$PWD" "$IMG" \
  latexmk -pdf -interaction=nonstopmode -halt-on-error fse27.tex
