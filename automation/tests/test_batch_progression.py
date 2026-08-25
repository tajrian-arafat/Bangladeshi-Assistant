"""Batch queue progression tests."""

from __future__ import annotations

from pathlib import Path

from automation.orchestrator.batch_manager import BatchManager


REPO = Path(__file__).resolve().parents[2]


def test_batch_queue_has_completed_and_ready() -> None:
    bm = BatchManager(REPO)
    queue = bm.generate_queue()
    ids = [b["batch_id"] for b in queue["batches"]]
    assert "BATCH_01" in ids
    assert "BATCH_02A" in ids
    assert "BATCH_02B" in ids
    assert "BATCH_03A" in ids
    batch_01 = next(b for b in queue["batches"] if b["batch_id"] == "BATCH_01")
    batch_03a = next(b for b in queue["batches"] if b["batch_id"] == "BATCH_03A")
    assert batch_01["status"] == "COMPLETE"
    assert batch_03a["status"] == "READY"
    assert len(batch_03a["service_ids"]) == 6


def test_next_ready_batch() -> None:
    bm = BatchManager(REPO)
    bm.write_queue()
    ready = bm.next_ready_batch()
    assert ready is not None
    assert ready["batch_id"] == "BATCH_03A"
