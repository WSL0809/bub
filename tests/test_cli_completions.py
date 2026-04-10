from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document

import bub.channels.cli as cli_module
from bub.channels.cli import CliChannel


def _get_completion_texts(completer, text: str) -> list[str]:
    doc = Document(text=text, cursor_position=len(text))
    return [c.text for c in completer.get_completions(doc, CompleteEvent())]


def test_cli_command_completer_matches_substring(monkeypatch, tmp_path: Path) -> None:
    # 端到端覆盖：验证 `CliChannel` 的补全在输入 `,` 后按子串实时匹配命令名。
    monkeypatch.setattr(
        cli_module,
        "REGISTRY",
        {"help": object(), "tape.info": object(), "tape.search": object(), "bash": object()},
        raising=False,
    )

    channel = CliChannel.__new__(CliChannel)
    channel._agent = SimpleNamespace(settings=SimpleNamespace(home=tmp_path), framework=SimpleNamespace(workspace=tmp_path))

    session = channel._build_prompt(tmp_path)
    completer = session.completer

    assert completer is not None
    assert ",help" in _get_completion_texts(completer, ",elp")
    assert ",tape.info" in _get_completion_texts(completer, ",ape")


def test_cli_command_completer_only_triggers_after_comma(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cli_module, "REGISTRY", {"help": object()}, raising=False)

    channel = CliChannel.__new__(CliChannel)
    channel._agent = SimpleNamespace(settings=SimpleNamespace(home=tmp_path), framework=SimpleNamespace(workspace=tmp_path))

    session = channel._build_prompt(tmp_path)
    completer = session.completer

    assert completer is not None
    assert _get_completion_texts(completer, "elp") == []
