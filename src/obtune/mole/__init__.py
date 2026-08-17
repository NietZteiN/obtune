"""Activation-space mixture over LoRA experts (Part III, the RouterLoRA experiment)."""
from obtune.mole.experts import ExpertBank, bank_summary, load_bank
from obtune.mole.gate import (
    ConstantGate, GateConfig, RouterGate, gate_entropy, one_hot_gate, summarise_routing,
    uniform_gate,
)
from obtune.mole.mixture import (
    MoLELinear, RoutingCtx, attach_mixture, freeze_all_but, one_hot_weights, uniform_weights,
)
from obtune.mole.eval_mole import HFEngine, routing_report
from obtune.mole.model import MoLEModel, attach_gate, build_mole_model

__all__ = [
    "ExpertBank", "load_bank", "bank_summary",
    "GateConfig", "RouterGate", "ConstantGate", "uniform_gate", "one_hot_gate",
    "gate_entropy", "summarise_routing",
    "MoLELinear", "RoutingCtx", "attach_mixture", "one_hot_weights", "uniform_weights",
    "freeze_all_but",
    "MoLEModel", "attach_gate", "build_mole_model",
    "HFEngine", "routing_report",
]
