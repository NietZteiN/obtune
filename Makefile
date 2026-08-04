# obtune — common entry points. See README.md and CLAUDE.md.
PY := /data/jvl210002/conda_envs/obtune/bin/python
export PYTHONPATH := src

.PHONY: help check test lint hooks testset corpus variants h1 pilot clean-pyc

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-12s %s\n", $$1, $$2}'

check: lint  ## Full integrity check: quarantine lint + SHA manifests + H1-marker scan
	$(PY) scripts/check_manifest.py
	$(PY) scripts/check_no_h1_in_train.py

test:  ## Run the test suite
	$(PY) -m pytest tests/

lint:  ## Quarantine-bypass lint only (fast)
	$(PY) -m pytest tests/test_quarantine_lint.py

hooks:  ## Install the pre-commit hook (runs `make check`)
	bash scripts/install_hooks.sh

testset:  ## Ingest the ICSE test set (70 L0 parents + 350 legacy rows)
	$(PY) scripts/01_ingest_testset.py

corpus:  ## Build the training corpus (sources -> filters -> inputs -> dedup -> splits)
	$(PY) scripts/02_build_corpus.py

variants:  ## Generate the 6 trainable conditions for train + test programs
	$(PY) scripts/05_build_variants.py

h1:  ## Generate the QUARANTINED held-out obfuscator variants
	$(PY) scripts/gen_h1_quarantined.py --i-am-the-h1-generator

pilot:  ## Week-1 kill-switch pilot (needs an idle GPU; check nvidia-smi first)
	bash scripts/run_pilot.sh

clean-pyc:
	find src scripts tests -name '__pycache__' -type d -exec rm -r {} + 2>/dev/null || true
