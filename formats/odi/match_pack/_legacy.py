"""Compatibility loader for the legacy match pack module."""
from __future__ import annotations

from functools import lru_cache
from importlib import util
from pathlib import Path
from types import ModuleType

_LEGACY_MODULE_NAME = "formats.odi._match_pack_legacy"


@lru_cache(maxsize=1)
def load_legacy_module() -> ModuleType:
    module_path = Path(__file__).resolve().parent / "_legacy_impl.py"
    spec = util.spec_from_file_location(_LEGACY_MODULE_NAME, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy match pack module from {module_path}")

    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def load_legacy_generator() -> type:
    module = load_legacy_module()
    generator = getattr(module, "MatchPackGenerator", None)
    if generator is None:
        raise ImportError("Legacy match pack module does not define MatchPackGenerator")
    return generator
