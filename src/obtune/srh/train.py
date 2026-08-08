"""Train one SRH arm.

    python -m obtune.srh.train --config srh/train/flip_qwen1.5b_py.yaml
    python -m obtune.srh.train --config srh/train/mix50_qwen1.5b_py.yaml --cpu --dry-run

A thin wrapper over `obtune.cft.train.main`, not a fork of it. The replication's trainer
already does everything needed — GPU pinning before torch, length filtering with a gated
drop rate, the loss-mask dry run, the provenance manifest — and the two experiments must
use the *same* recipe or any difference between their arms is a recipe difference. The
three injected hooks are the entire delta:

    load_mixture   -> srh.dataset.load_mixture   (adds `rev`, MIX50, common subsets)
    build_example  -> srh.prompts.build_example  (adds the `rev` target, symmetric arms)
    run_id_prefix  -> "srh"                      (so run ids never collide)

`cft.prompts` is untouched, so its guarantee that the replication's reverse direction is
never supervised still holds — and `srh.prompts.assert_replication_untouched()` fails the
job loudly if a future edit breaks it.
"""
from __future__ import annotations

import sys
from typing import Optional

from obtune.cft import train as cft_train
from obtune.srh import dataset as srh_data
from obtune.srh import prompts as srh_prompts


def main(argv: Optional[list[str]] = None) -> int:
    srh_prompts.assert_replication_untouched()

    # `symmetric` is a property of the arm, not of the data, so it is bound into the
    # example builder rather than stored on every row (see prompts.build_example_factory).
    args = cft_train.build_parser().parse_args(argv)
    from obtune.config import load_config

    cfg = load_config(args.config)
    builder = srh_prompts.build_example_factory(bool(cfg.get("symmetric", False)))

    return cft_train.main(
        argv,
        load_mixture=srh_data.load_mixture,
        build_example=builder,
        run_id_prefix="srh",
    )


if __name__ == "__main__":
    sys.exit(main())
