from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document


@dataclass(frozen=True, slots=True)
class CommaCommandCompleter(Completer):
    """仅用于以 `,` 开头的内部命令补全。

    匹配规则：去掉前导 `,` 后，对命令名做不区分大小写的“子串命中”。
    例如输入 `,elp` 也能匹配到 `,help`。
    """

    command_words: tuple[str, ...]

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        word = document.get_word_before_cursor(WORD=True)
        if not word.startswith(","):
            return

        start = document.cursor_position - len(word)
        if start != 0:
            return

        query = word[1:].casefold()
        matches: list[tuple[int, int, str]] = []
        for candidate in self.command_words:
            if not candidate.startswith(","):
                continue
            haystack = candidate[1:].casefold()
            if not query:
                matches.append((0, len(haystack), candidate))
                continue
            idx = haystack.find(query)
            if idx != -1:
                matches.append((idx, len(haystack), candidate))

        matches.sort()
        for _, __, candidate in matches:
            yield Completion(candidate, start_position=-len(word))
