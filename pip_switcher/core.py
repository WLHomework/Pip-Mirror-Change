#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core logic: manage pip mirrors using `pip config`.
"""
from __future__ import annotations
import subprocess
import sys
from typing import Dict, Tuple

MIRRORS: Dict[str, Tuple[str, str]] = {
    "tsinghua": ("https://pypi.tuna.tsinghua.edu.cn/simple", "pypi.tuna.tsinghua.edu.cn"),
    "aliyun": ("https://mirrors.aliyun.com/pypi/simple", "mirrors.aliyun.com"),
    "huawei": ("https://mirrors.huaweicloud.com/repository/pypi/simple", "repo.huaweicloud.com"),
    "tencent": ("https://mirrors.cloud.tencent.com/pypi/simple", "mirrors.cloud.tencent.com"),
    "ustc": ("https://pypi.mirrors.ustc.edu.cn/simple", "pypi.mirrors.ustc.edu.cn"),
    "douban": ("https://pypi.doubanio.com/simple", "pypi.doubanio.com"),
}


def _scope_flag(scope: str) -> str:
    if scope not in {"user", "global", "site"}:
        raise ValueError("scope must be one of: user, global, site")
    return f"--{scope}"


def _run_pip_config(args: list[str]) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "pip", "config"] + args
    return subprocess.run(cmd, capture_output=True, text=True)


def set_mirror(name: str, scope: str) -> None:
    index_url, host = MIRRORS[name]
    res1 = _run_pip_config(["set", _scope_flag(scope), "global.index-url", index_url])
    if res1.returncode != 0:
        msg = "[ERROR] Failed to set index-url:\n" + (res1.stderr or res1.stdout)
        raise RuntimeError(msg)
    res2 = _run_pip_config(["set", _scope_flag(scope), "global.trusted-host", host])
    if res2.returncode != 0:
        # Warn only
        print("[WARN] Failed to set trusted-host (you may ignore if SSL works):\n" + (res2.stderr or res2.stdout))
    print(f"[OK] Switched pip to '{name}' mirror: {index_url} (scope={scope})")


def reset_mirror(scope: str) -> None:
    _run_pip_config(["unset", _scope_flag(scope), "global.index-url"])  # remove index-url
    _run_pip_config(["unset", _scope_flag(scope), "global.trusted-host"])  # remove trusted-host
    print(f"[OK] Reset pip config to default (scope={scope})")


def show_config() -> None:
    res = _run_pip_config(["list"])
    if res.returncode != 0:
        msg = "[ERROR] Failed to read pip config:\n" + (res.stderr or res.stdout)
        raise RuntimeError(msg)
    lines = (res.stdout or "").splitlines()
    interesting = [
        l for l in lines if any(k in l for k in ["global.index-url", "global.trusted-host", "index-url", "trusted-host"])
    ]
    print("\n".join(interesting) if interesting else res.stdout)


def get_effective_index_url() -> str | None:
    """Return the effective pip index-url if set, else None.
    Parses `pip config list` output for any `index-url` entry.
    """
    res = _run_pip_config(["list"])
    if res.returncode != 0:
        return None
    out = res.stdout or ""
    for line in out.splitlines():
        if "index-url" in line and "=" in line:
            # format like: global.index-url='https://...'
            val = line.split("=", 1)[1].strip()
            if val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            return val
    return None
