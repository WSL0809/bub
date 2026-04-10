from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document

import bub.channels.cli as cli_module
from bub.channels.cli import CliChannel
from bub.channels.cli.completer import CommaCommandCompleter


def _get_completion_texts(completer, text: str) -> list[str]:
    doc = Document(text=text, cursor_position=len(text))
    return [c.text for c in completer.get_completions(doc, CompleteEvent())]


def test_cli_command_completer_matches_prefix(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        cli_module,
        "REGISTRY",
        {"help": object(), "tape.info": object(), "tape.search": object(), "bash": object()},
        raising=False,
    )

    channel = CliChannel.__new__(CliChannel)
    channel._agent = SimpleNamespace(
        settings=SimpleNamespace(home=tmp_path), framework=SimpleNamespace(workspace=tmp_path)
    )

    session = channel._build_prompt(tmp_path)
    completer = session.completer

    assert completer is not None
    assert ",help" in _get_completion_texts(completer, ",hel")
    assert ",tape.info" in _get_completion_texts(completer, ",ta")


def test_cli_command_completer_only_triggers_after_comma(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cli_module, "REGISTRY", {"help": object()}, raising=False)

    channel = CliChannel.__new__(CliChannel)
    channel._agent = SimpleNamespace(
        settings=SimpleNamespace(home=tmp_path), framework=SimpleNamespace(workspace=tmp_path)
    )

    session = channel._build_prompt(tmp_path)
    completer = session.completer

    assert completer is not None
    assert _get_completion_texts(completer, "elp") == []


def test_cli_command_completer_keeps_working_when_word_boundary_drops_comma() -> None:
    class FakeDocument:
        def __init__(self, text: str, word_before_cursor: str) -> None:
            self.text = text
            self.text_before_cursor = text
            self.cursor_position = len(text)
            self._word_before_cursor = word_before_cursor

        def get_word_before_cursor(self, WORD: bool = True) -> str:
            return self._word_before_cursor

    completer = CommaCommandCompleter((",help",))
    completions = [c.text for c in completer.get_completions(FakeDocument(",hel", "hel"), CompleteEvent())]
    assert completions == [",help"]


def test_cli_command_completer_completes_when_args_exist() -> None:
    completer = CommaCommandCompleter((",help",))
    doc = Document(text=",hel query=1", cursor_position=4)
    assert [c.text for c in completer.get_completions(doc, CompleteEvent())] == [",help"]


def test_delete_before_cursor_triggers_completion_for_internal_commands() -> None:
    from bub.channels.cli import _delete_before_cursor_and_complete

    calls: list[str] = []

    class FakeBuffer:
        def __init__(self, text: str) -> None:
            self.text = text

        def delete_before_cursor(self, *, count: int) -> None:
            assert count == 1
            self.text = self.text[:-1]
            calls.append("delete")

        def start_completion(self, *, select_first: bool) -> None:
            assert select_first is False
            calls.append("complete")

    buffer = FakeBuffer(",helx")
    _delete_before_cursor_and_complete(buffer)

    assert buffer.text == ",hel"
    assert calls == ["delete", "complete"]
