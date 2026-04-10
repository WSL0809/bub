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
        text = document.text
        before = document.text_before_cursor

        if not text.startswith(","):
            return

        # 只在“行首 internal command”补全：光标必须处在第一个 token 的末尾（空白字符之前），
        # 或者已经到达行尾。这样补全替换不会意外拼接/重复后缀。
        if any(ch.isspace() for ch in before):
            return

        cursor = document.cursor_position
        if cursor < len(text) and not text[cursor].isspace():
            return

        typed = before
        query = typed[1:].casefold()
        start_position = -len(typed)

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
            yield Completion(candidate, start_position=start_position)
