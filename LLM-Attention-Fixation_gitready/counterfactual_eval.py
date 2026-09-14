from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


_MODULE_PATH = Path(__file__).resolve().parent / "evaluation" / "java_counterfactual.py"
_SPEC = importlib.util.spec_from_file_location("_cf_eval_impl", _MODULE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Failed to load counterfactual module from {_MODULE_PATH}")
_MOD = importlib.util.module_from_spec(_SPEC)
# Ensure decorators (e.g. dataclass) can resolve module metadata during dynamic load.
sys.modules[_SPEC.name] = _MOD
_SPEC.loader.exec_module(_MOD)

build_case_pack = _MOD.build_case_pack
build_counterfactual_instruction = _MOD.build_counterfactual_instruction
parse_predicted_labels = _MOD.parse_predicted_labels
resolve_task_profile = _MOD.resolve_task_profile
score_case_predictions = _MOD.score_case_predictions
