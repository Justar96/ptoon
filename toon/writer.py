from .types import Depth


class LineWriter:
    def __init__(self, indent_size: int):
        self.lines: list[str] = []
        self.indentation_string = " " * indent_size
        self._indent_cache: dict[int, str] = {0: ""}

    def push(self, depth: Depth, content: str):
        if depth not in self._indent_cache:
            self._indent_cache[depth] = self.indentation_string * depth
        indent = self._indent_cache[depth]
        self.lines.append(indent + content)

    def to_string(self) -> str:
        return "\n".join(self.lines)
