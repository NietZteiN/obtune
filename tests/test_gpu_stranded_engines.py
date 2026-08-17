"""The GPU deadlock that no other mechanism recovers from.

On 2026-08-11 four eval jobs were killed. vLLM's `VLLM::EngineCore` children were reparented
to init and kept their ~41 GB KV-cache reservations, so all four GPUs sat at 0% utilisation
holding 164 GB while seven jobs waited in the queue. The worker refuses any GPU with >2 GB
used — correctly, since it cannot distinguish a live neighbour from a corpse — so the queue
could never drain. `--sweep-orphans` did not help: it returns stranded manifest CLAIMS, and
the claim had already been returned. It is the GPU that is stuck, not the claim.

These tests pin the three discriminations that make automatic reaping safe on a SHARED box,
because each one is the difference between self-healing and killing someone else's job.
"""
from __future__ import annotations

import pytest

from obtune import gpu_alloc


@pytest.fixture()
def fake_procs(monkeypatch, tmp_path):
    """Drive the scan from a table instead of /proc, so orphans can be simulated."""
    table: dict[int, dict] = {}

    def setup(procs: dict[int, list[int]], meta: dict[int, dict]):
        table.clear()
        table.update(meta)
        monkeypatch.setattr(gpu_alloc, "_compute_apps", lambda: procs)
        monkeypatch.setattr(gpu_alloc, "_same_uid", lambda pid: table[pid]["mine"])
        monkeypatch.setattr(gpu_alloc, "_ppid", lambda pid: table[pid]["ppid"])

        class _P:
            def __init__(self, path): self.path = str(path)
            def __truediv__(self, other): return self
            def read_text(self):
                pid = int(self.path.rsplit("/", 1)[1])
                return table[pid]["comm"]

        monkeypatch.setattr(gpu_alloc, "Path", _P)
        # No manifest claims unless a test says otherwise.
        monkeypatch.setattr(gpu_alloc, "RUNS_DIR", tmp_path, raising=False)

    return setup


def test_reaps_our_orphaned_engine(fake_procs) -> None:
    """The actual incident: ours, ppid==1, a vLLM engine, on a GPU with no claim."""
    fake_procs({0: [999]}, {999: {"mine": True, "ppid": 1, "comm": "VLLM::EngineCor"}})
    found = gpu_alloc.stranded_engines(require_no_claim=False)
    assert [r["pid"] for r in found] == [999]
    assert found[0]["gpu"] == 0


def test_never_touches_another_users_process(fake_procs) -> None:
    """Shared box, no scheduler. Reaping a neighbour's job is the worst outcome here —
    strictly worse than the deadlock this feature exists to break."""
    fake_procs({0: [999]}, {999: {"mine": False, "ppid": 1, "comm": "VLLM::EngineCor"}})
    assert gpu_alloc.stranded_engines(require_no_claim=False) == []


def test_never_touches_a_live_engine(fake_procs) -> None:
    """A real parent means a running job, however idle the GPU looks. The four live engines
    on this box during the incident all had ppid == their eval process."""
    fake_procs({0: [999]}, {999: {"mine": True, "ppid": 4242, "comm": "VLLM::EngineCor"}})
    assert gpu_alloc.stranded_engines(require_no_claim=False) == []


def test_never_touches_a_non_engine(fake_procs) -> None:
    """An orphaned shell of ours holding a GPU is not something this should decide about."""
    fake_procs({0: [999]}, {999: {"mine": True, "ppid": 1, "comm": "python3.12"}})
    assert gpu_alloc.stranded_engines(require_no_claim=False) == []


def test_skips_a_gpu_that_still_has_a_claim(fake_procs, tmp_path, monkeypatch) -> None:
    """The decisive safety condition. If a worker holds the claim, the GPU is in use even if
    a pid momentarily looks orphaned — reaping there would kill live work."""
    claim = tmp_path / "manifest" / "running" / "gpu0"
    claim.mkdir(parents=True)
    (claim / "job.json").write_text("{}")
    fake_procs({0: [999]}, {999: {"mine": True, "ppid": 1, "comm": "VLLM::EngineCor"}})
    monkeypatch.setattr(gpu_alloc, "RUNS_DIR", tmp_path, raising=False)
    monkeypatch.setattr("obtune.config.RUNS_DIR", tmp_path, raising=False)
    assert gpu_alloc.stranded_engines(require_no_claim=True) == []
    # ...and the same pid IS reported once the claim is gone.
    (claim / "job.json").unlink()
    claim.rmdir()
    assert [r["pid"] for r in gpu_alloc.stranded_engines(require_no_claim=True)] == [999]


def test_dry_run_kills_nothing(fake_procs, monkeypatch) -> None:
    fake_procs({0: [999]}, {999: {"mine": True, "ppid": 1, "comm": "VLLM::EngineCor"}})
    killed: list[int] = []
    monkeypatch.setattr("os.kill", lambda pid, sig: killed.append(pid))
    monkeypatch.setattr(gpu_alloc, "stranded_engines",
                        lambda *a, **k: [{"pid": 999, "gpu": 0, "comm": "VLLM::EngineCor"}])
    assert gpu_alloc.reap_stranded_engines(dry_run=True) == [
        {"pid": 999, "gpu": 0, "comm": "VLLM::EngineCor"}]
    assert killed == [], "dry_run must not signal anything"
