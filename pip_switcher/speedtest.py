#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mirror speed test utilities (no external deps).
Measures latency by performing a lightweight HTTP GET to the mirror's /simple index.
"""
from __future__ import annotations
import time
import urllib.request
import urllib.error
from typing import Dict, Tuple, List, Callable, Optional

# Type alias for clarity
MirrorMap = Dict[str, Tuple[str, str]]  # name -> (index_url, host)


def _probe(url: str, timeout: float = 3.5) -> float:
    """Return elapsed seconds for a GET to url, or float('inf') on failure."""
    start = time.perf_counter()
    req = urllib.request.Request(url, headers={
        "User-Agent": "pip-mirror-switcher/1.0 (+https://python.org)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "close",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # Read a small chunk then close
            resp.read(128)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return float("inf")
    except Exception:
        return float("inf")
    else:
        return time.perf_counter() - start


def benchmark_mirrors(
    mirrors: MirrorMap,
    attempts: int = 2,
    timeout: float = 3.5,
    progress: Optional[Callable[[str], None]] = None,
) -> List[Tuple[str, float]]:
    """
    Benchmark mirrors and return a list of (name, avg_ms) sorted by fastest.
    - attempts: number of probes per mirror; uses min latency to reduce noise
    - timeout: per-request timeout seconds
    """
    results: List[Tuple[str, float]] = []
    for name, (index_url, _host) in mirrors.items():
        if progress:
            progress(f"正在测试 {name} 源…")
        target = index_url.rstrip("/") + "/"  # ensure trailing slash to hit /simple/
        samples = []
        for _ in range(attempts):
            elapsed = _probe(target, timeout=timeout)
            samples.append(elapsed)
        best = min(samples) if samples else float("inf")
        avg_ms = best * 1000.0 if best != float("inf") else float("inf")
        results.append((name, avg_ms))
    # sort, treating inf as very large
    results.sort(key=lambda x: (x[1] == float("inf"), x[1]))
    if progress:
        progress("测速完成。正在计算推荐结果…")
    return results


def format_ranking(ranking: List[Tuple[str, float]]) -> str:
    lines = ["测速结果（单位：ms，越小越好）:"]
    for i, (name, ms) in enumerate(ranking, 1):
        human = "超时/失败" if ms == float("inf") else f"{ms:.0f}ms"
        lines.append(f"{i:>2}. {name:<8}  {human}")
    return "\n".join(lines)
