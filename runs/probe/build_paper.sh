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
cd "paper/${1:-paper_latex}"
singularity exec -B "$PWD:$PWD" --pwd "$PWD" "$IMG" \
  latexmk -pdf -interaction=nonstopmode -halt-on-error fse27.tex
