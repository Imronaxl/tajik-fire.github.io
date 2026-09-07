from typing import Callable, Dict, List, Optional

from fastapi import APIRouter


class ModuleManifest:
    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        router_factory: Optional[Callable[[], APIRouter]] = None,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
    ):
        self.name = name
        self.version = version
        self.description = description
        self.router_factory = router_factory
        self.prefix = prefix
        self.tags = tags or [name]
        self.depends_on = depends_on or []


_registry: Dict[str, ModuleManifest] = {}


def register_module(manifest: ModuleManifest) -> None:
    if manifest.name in _registry:
        raise ValueError(f"module '{manifest.name}' is already registered")
    _registry[manifest.name] = manifest


def get_module(name: str) -> Optional[ModuleManifest]:
    return _registry.get(name)


def list_modules() -> List[ModuleManifest]:
    return list(_registry.values())


def get_all_routers() -> List[tuple]:
    out = []
    for manifest in _registry.values():
        if manifest.router_factory:
            out.append((manifest.router_factory(), manifest.prefix, manifest.tags))
    return out
