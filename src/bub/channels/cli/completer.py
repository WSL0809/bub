from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document


@dataclass(frozen=True, slots=True)
class CommaCommandCompleter(Completer):
    command_words: tuple[str, ...]

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        text = document.text
        before = document.text_before_cursor

        if not text.startswith(","):
            return

        if any(ch.isspace() for ch in before):
            return

        cursor = document.cursor_position
        if cursor < len(text) and not text[cursor].isspace():
            return

        typed = before
        query = typed[1:].casefold()
        start_position = -len(typed)

        matches: list[tuple[int, str]] = []
        for candidate in self.command_words:
            if not candidate.startswith(","):
                continue
            haystack = candidate[1:].casefold()
            if not query:
                matches.append((len(haystack), candidate))
                continue
            if haystack.startswith(query):
                matches.append((len(haystack), candidate))

        matches.sort()
        for _, candidate in matches:
            yield Completion(candidate, start_position=start_position)
