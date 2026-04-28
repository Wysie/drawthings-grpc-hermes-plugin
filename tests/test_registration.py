"""Minimal smoke tests for plugin registration without requiring a live Draw Things server."""

import importlib.util
import pathlib
import sys


class DummyCtx:
    def __init__(self):
        self.tools = []
        self.skills = []

    def register_tool(self, **kwargs):
        self.tools.append(kwargs)

    def register_skill(self, name, path):
        self.skills.append((name, path))


def test_registers_tools():
    root = pathlib.Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "drawthings_grpc_plugin",
        root / "__init__.py",
        submodule_search_locations=[str(root)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    ctx = DummyCtx()
    module.register(ctx)

    names = {tool["name"] for tool in ctx.tools}
    assert "drawthings_list" in names
    assert "drawthings_generate" in names
    assert all(tool["toolset"] == "drawthings" for tool in ctx.tools)
    assert all("parameters" in tool["schema"] for tool in ctx.tools)
