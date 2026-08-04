#!/usr/bin/env python3
"""Update publication citation counts from Wanyi Chen's Google Scholar profile."""

from __future__ import annotations

import json
import os
import re
import signal
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from scholarly import scholarly

ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "data" / "metrics.json"
SCHOLAR_USER_ID = "e_gM0k8AAAAJ"

PUBLICATION_TITLES = {
    "ai4ai-at-scale": "AI4AI at Scale: A Full-Pipeline System for Enhancing LLM Agentic Capabilities",
    "evm-questbench": "EVM-QuestBench: An Execution-Grounded Benchmark for Natural-Language Transaction Code Generation",
    "on-device-llms": "On-Device Large Language Models: A Survey of Model Compression and System Optimization",
    "agent2-rl-bench": "Agent2 RL-Bench: Can LLM Agents Engineer Agentic RL Post-Training?",
    "twinrouterbench": "TwinRouterBench: Fast Static and Live Dynamic Evaluation for Realistic Agentic LLM Routing",
    "structured-output-attribution": "Attributing Structured-Output Gains in Function Calling: Interface Alignment versus Procedural Transfer",
    "aoi": "AOI: Turning Failed Trajectories into Training Signals for Autonomous Cloud Diagnosis",
}


def normalize_title(title: str) -> str:
    text = unicodedata.normalize("NFKD", title).casefold().replace("²", "2")
    return re.sub(r"[^a-z0-9]+", "", text)


def load_metrics() -> dict:
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return {"publications": {}}


def fetch_scholar_counts() -> dict[str, int]:
    scholarly.set_timeout(10)
    scholarly.set_retries(1)
    author = scholarly.search_author_id(SCHOLAR_USER_ID)
    author = scholarly.fill(author, sections=["publications"])

    scholar_counts: dict[str, int] = {}
    for publication in author.get("publications", []):
        title = publication.get("bib", {}).get("title", "")
        if title:
            scholar_counts[normalize_title(title)] = int(publication.get("num_citations", 0))
    return scholar_counts


def main() -> None:
    timeout_seconds = int(os.environ.get("SCHOLAR_UPDATE_TIMEOUT", "90"))

    def handle_timeout(_signum: int, _frame: object) -> None:
        raise TimeoutError(f"Google Scholar request exceeded {timeout_seconds} seconds")

    previous_handler = signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(timeout_seconds)
    try:
        scholar_counts = fetch_scholar_counts()
    except Exception as exc:
        print(
            "::warning title=Google Scholar update skipped::"
            f"{type(exc).__name__}: {exc}. Existing metrics were preserved."
        )
        return
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)

    metrics = load_metrics()
    publications = metrics.setdefault("publications", {})
    matched = 0

    for publication_id, title in PUBLICATION_TITLES.items():
        citation_count = scholar_counts.get(normalize_title(title))
        if citation_count is None:
            continue
        entry = publications.setdefault(publication_id, {})
        entry["citations"] = citation_count
        matched += 1

    if matched == 0:
        print(
            "::warning title=Google Scholar update skipped::"
            "No homepage publications matched the profile. Existing metrics were preserved."
        )
        return

    metrics["source"] = "Google Scholar"
    metrics["scholar_user_id"] = SCHOLAR_USER_ID
    metrics["updated_at"] = datetime.now(timezone.utc).date().isoformat()
    METRICS_PATH.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {matched}/{len(PUBLICATION_TITLES)} publication citation counts.")


if __name__ == "__main__":
    main()
