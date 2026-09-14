"""Every panel model must be constructible as a mixture, without loading weights.

Three separate bugs on 2026-09-14 stopped the mixture arm existing off CodeLlama, each found only by
running a two-hour job for twelve minutes: a raw chat template (CodeGemma: "System role not
supported"), `config.hidden_size` absent on multimodal `Gemma3Config`, and the decoder layer list
living under `model.language_model.layers` on the same model. All three are answerable from the
config and a meta-device instantiation in under a second, so they belong in a test rather than in a
GPU queue.
"""
import pytest
import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from obtune import prompts
from obtune.config import load_config
from obtune.mole.model import _decoder_layers, _hidden_size

PANEL = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
         "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]
HF = {k: v["hf_id"] for k, v in load_config("models.yaml")["models"].items()}


@pytest.mark.parametrize("model_key", PANEL)
def test_mixture_shape_is_discoverable(model_key):
    """hidden_size and the decoder layer list resolve for every panel model."""
    cfg = AutoConfig.from_pretrained(HF[model_key])
    assert _hidden_size(cfg) > 0
    with torch.device("meta"):
        m = AutoModelForCausalLM.from_config(cfg)
    layers = _decoder_layers(m)
    assert len(layers) > 0, f"{model_key}: no decoder layers found"


@pytest.mark.parametrize("model_key", PANEL)
def test_gate_training_renders_through_the_adaptation_layer(model_key):
    """render_pair must not hand a system role to a template that refuses one."""
    from obtune.mole.train_mole import render_pair
    tok = AutoTokenizer.from_pretrained(HF[model_key])
    rec = {"prompt": [{"role": "system", "content": "SYSMARK"},
                      {"role": "user", "content": "U"}],
           "completion": [{"role": "assistant", "content": "A"}]}
    prompt, full = render_pair(tok, rec)          # must not raise
    assert "SYSMARK" in prompt, f"{model_key}: system text lost in {prompts.template_mode(tok)} mode"
    assert full.startswith(prompt[:40])
