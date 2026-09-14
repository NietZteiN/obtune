#!/usr/bin/env python3
"""
Utility script to inspect the architecture configuration of the CodeLlama model
used in the attention experiments. Example usage:

    python3 model_info.py
    python3 model_info.py --model codellama/CodeLlama-70b-Instruct-hf --cache-dir /path/to/cache
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional


DEFAULT_MODEL_NAME = "codellama/CodeLlama-70b-Instruct-hf"


def _load_config(model_name: str, cache_dir: Optional[str]) -> Any:
    """
    Attempt to load the Hugging Face config for the requested model.
    """
    try:
        from transformers import AutoConfig  # type: ignore
    except ImportError as exc:  # pragma: no cover - informative message for missing deps
        print(
            "Unable to import 'transformers'. Install it first, e.g.:\n"
            "    pip install transformers accelerate safetensors\n",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    config = AutoConfig.from_pretrained(
        model_name,
        cache_dir=cache_dir,
        local_files_only=True,
    )
    return config


def _summarise_config(cfg: Any) -> Dict[str, Any]:
    """
    Pull out the key architectural fields we normally care about.
    """
    summary = {
        "model_type": getattr(cfg, "model_type", None),
        "hidden_size": getattr(cfg, "hidden_size", None),
        "intermediate_size": getattr(cfg, "intermediate_size", None),
        "num_hidden_layers": getattr(cfg, "num_hidden_layers", None),
        "num_attention_heads": getattr(cfg, "num_attention_heads", None),
        "num_key_value_heads": getattr(cfg, "num_key_value_heads", None),
        "vocab_size": getattr(cfg, "vocab_size", None),
        "rope_theta": getattr(cfg, "rope_theta", None),
        "max_position_embeddings": getattr(cfg, "max_position_embeddings", None),
    }
    return summary


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Inspect the CodeLlama architecture configuration.")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_NAME,
        help=f"Hugging Face model identifier (default: {DEFAULT_MODEL_NAME!r})",
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Optional path to the local HF cache directory (uses environment defaults when omitted).",
    )
    args = parser.parse_args(argv)

    cfg = _load_config(args.model, args.cache_dir)

    print("=== Raw configuration ===")
    print(cfg)
    print()

    summary = _summarise_config(cfg)
    print("=== Key fields ===")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
