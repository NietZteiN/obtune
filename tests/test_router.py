"""CPU unit tests for the RQ2 router (synthetic features — no GPU, no model download).

Synthetic design: 6 well-separated Gaussian class centroids in 64-D, plus a 7th
"H1-like" centroid placed at the mean of the six so that a correct implementation must
route it with HIGH entropy. Programs are the split unit: every program contributes one
row per condition, which is exactly the correlation structure that makes row-wise
splitting leak.
"""
from __future__ import annotations

import numpy as np
import pytest

from obtune.paths import TRAINABLE_CONDITIONS
from obtune.router.features import CONDITION_TO_LABEL, H1_LABEL, FeatureSet, load_features, save_features
from obtune.router.route import confusion_matrix, entropy_report, route_features
from obtune.router.train_router import (
    RouterCheckpoint,
    load_checkpoint,
    save_checkpoint,
    split_by_program,
    train_router,
)

D = 64
N_PROGRAMS = 120


def _synth(seed: int = 17, include_h1: bool = True, sep: float = 3.0) -> FeatureSet:
    rng = np.random.default_rng(seed)
    centroids = rng.normal(size=(len(TRAINABLE_CONDITIONS), D)) * sep
    h1_centroid = centroids.mean(axis=0)  # deliberately ambiguous

    X, y, items, progs, conds, langs = [], [], [], [], [], []
    conditions = list(TRAINABLE_CONDITIONS) + (["H1"] if include_h1 else [])
    for p in range(N_PROGRAMS):
        lang = "python" if p % 2 == 0 else "javascript"
        # per-program offset: rows of one program are correlated (the leakage hazard)
        off = rng.normal(size=D) * 0.6
        for c in conditions:
            mu = h1_centroid if c == "H1" else centroids[CONDITION_TO_LABEL[c]]
            X.append(mu + off + rng.normal(size=D))
            y.append(H1_LABEL if c == "H1" else CONDITION_TO_LABEL[c])
            items.append(f"prog{p:04d}::{c}::0")
            progs.append(f"prog{p:04d}")
            conds.append(c)
            langs.append(lang)
    return FeatureSet(
        X=np.asarray(X, dtype=np.float32), y=np.asarray(y, dtype=np.int16),
        item_ids=np.asarray(items), program_ids=np.asarray(progs),
        conditions=np.asarray(conds), languages=np.asarray(langs),
        meta={"synthetic": True, "layer": 14, "class_order": list(TRAINABLE_CONDITIONS)},
    )


def test_split_is_by_program_not_row():
    fs = _synth()
    tr, va = split_by_program(fs.program_ids, val_fraction=0.2, seed=17)
    assert tr.sum() > 0 and va.sum() > 0
    assert not (set(fs.program_ids[tr]) & set(fs.program_ids[va])), "program leaked across splits"
    # every program contributes all of its rows to exactly one side
    assert tr.sum() + va.sum() == len(fs)


def test_h1_is_never_a_class():
    fs = _synth()
    assert "H1" not in CONDITION_TO_LABEL
    ck = train_router(fs, max_epochs=8, early_stop_patience=8, seed=17, verbose=False)
    assert ck.n_classes == len(TRAINABLE_CONDITIONS)
    assert ck.class_order == list(TRAINABLE_CONDITIONS)
    assert ck.meta["n_train"] + ck.meta["n_val"] == int(fs.trainable_mask().sum())


def test_router_learns_separable_classes():
    fs = _synth()
    ck = train_router(fs, max_epochs=30, early_stop_patience=5, seed=17, verbose=False)
    assert ck.val_accuracy > 0.90, f"val accuracy {ck.val_accuracy} too low on separable data"
    assert ck.best_epoch >= 0
    assert len(ck.history) >= 1


def test_checkpoint_roundtrip(tmp_path):
    fs = _synth()
    ck = train_router(fs, max_epochs=6, early_stop_patience=6, seed=17, verbose=False)
    p = save_checkpoint(ck, tmp_path / "router.npz")
    ck2 = load_checkpoint(p)
    assert ck2.in_dim == ck.in_dim and ck2.class_order == ck.class_order
    np.testing.assert_allclose(ck2.mean, ck.mean)
    rows1 = route_features(fs, ck)
    rows2 = route_features(fs, ck2)
    assert [r["routed_condition"] for r in rows1] == [r["routed_condition"] for r in rows2]


def test_features_npz_roundtrip(tmp_path):
    fs = _synth()
    p = save_features(fs, tmp_path / "feat.npz")
    fs2 = load_features(p)
    np.testing.assert_allclose(fs.X, fs2.X)
    assert list(fs2.conditions[:3]) == list(fs.conditions[:3])
    assert fs2.meta["class_order"] == list(TRAINABLE_CONDITIONS)


def test_routing_outputs_and_entropy_report():
    fs = _synth()
    ck = train_router(fs, max_epochs=30, early_stop_patience=5, seed=17, verbose=False)
    rows = route_features(fs, ck, adapter_map={c: f"lora_{c}" for c in TRAINABLE_CONDITIONS})

    r = rows[0]
    assert set(["item_id", "adapter", "entropy", "routed_condition"]) <= set(r)
    assert r["adapter"].startswith("lora_")
    probs = np.array([[row[f"p_{c}"] for c in TRAINABLE_CONDITIONS] for row in rows])
    np.testing.assert_allclose(probs.sum(axis=1), 1.0, atol=1e-6)
    assert (probs >= 0).all()

    cm = confusion_matrix(rows)
    assert "H1" in cm and sum(cm["H1"].values()) == N_PROGRAMS
    for c in TRAINABLE_CONDITIONS:
        assert sum(cm[c].values()) == N_PROGRAMS

    rep = entropy_report(rows)
    assert rep["n_heldout"] == N_PROGRAMS
    assert rep["per_condition"]["H1"]["route_accuracy"] is None  # H1 has no correct route
    # the H1 centroid sits at the mean of the six => its routing entropy must exceed
    # the held-in conditions', which is the RQ2 "does the router know it is lost" check
    assert rep["mannwhitney"]["delta_mean_entropy"] > 0
    assert rep["mannwhitney"]["p"] < 0.01


def test_router_rejects_dim_mismatch():
    fs = _synth()
    ck = train_router(fs, max_epochs=3, early_stop_patience=3, seed=17, verbose=False)
    bad = fs.subset(np.ones(len(fs), dtype=bool))
    bad.X = bad.X[:, :16]
    with pytest.raises(ValueError):
        route_features(bad, ck)


def test_seed_determinism():
    fs = _synth()
    a = train_router(fs, max_epochs=6, early_stop_patience=6, seed=17, verbose=False)
    b = train_router(fs, max_epochs=6, early_stop_patience=6, seed=17, verbose=False)
    assert a.val_accuracy == b.val_accuracy
    for k in a.state_dict:
        np.testing.assert_allclose(a.state_dict[k], b.state_dict[k], rtol=1e-6, atol=1e-6)
