from __future__ import annotations

import json
import shutil
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _val(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, list):
        return "[" + ", ".join(_val(x) for x in v) + "]"
    raise TypeError(type(v))


def _is_table_list(v: Any) -> bool:
    return isinstance(v, list) and bool(v) and all(isinstance(x, dict) for x in v)


def _key(k: str) -> str:
    return (
        k if k.replace("_", "a").replace("-", "a").isalnum() and not k.isdigit() else json.dumps(k)
    )


def dumps(data: dict[str, Any]) -> str:
    """A small TOML writer, enough for catalog-shaped data."""
    out: list[str] = []

    def emit(path: str, table: dict[str, Any], array: bool) -> None:
        out.append(f"[[{path}]]" if array else f"[{path}]")
        for k, v in table.items():
            if not isinstance(v, dict) and not _is_table_list(v):
                out.append(f"{_key(k)} = {_val(v)}")
        for k, v in table.items():
            if isinstance(v, dict):
                emit(f"{path}.{_key(k)}", v, False)
            elif _is_table_list(v):
                for item in v:
                    emit(f"{path}.{_key(k)}", item, True)
        out.append("")

    for k, v in data.items():
        if isinstance(v, dict):
            emit(_key(k), v, False)
        elif _is_table_list(v):
            for item in v:
                emit(_key(k), item, True)
    return "\n".join(out)


@pytest.fixture(scope="session")
def real() -> dict[str, Any]:
    return tomllib.loads((ROOT / "catalog" / "platform.toml").read_text())


@pytest.fixture
def make_catalog(tmp_path: Path, real: dict[str, Any]) -> Callable[..., Path]:
    """Write a mutated copy of the real catalog (with its docs) and return its path."""
    shutil.copytree(ROOT / "docs", tmp_path / "docs", ignore=shutil.ignore_patterns("generated"))

    def _make(mutate: Callable[[dict[str, Any]], None] | None = None) -> Path:
        data = json.loads(json.dumps(real))
        if mutate:
            mutate(data)
        path = tmp_path / "catalog" / "platform.toml"
        path.parent.mkdir(exist_ok=True)
        path.write_text(dumps(data), encoding="utf-8")
        return path

    return _make


def comp(data: dict[str, Any], cid: str) -> dict[str, Any]:
    return next(c for c in data["components"] if c["id"] == cid)


def edge(data: dict[str, Any], source: str, target: str) -> dict[str, Any]:
    return next(e for e in comp(data, source)["depends_on"] if e["target"] == target)
