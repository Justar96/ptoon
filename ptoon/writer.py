from .types import Depth


class LineWriter:
    def __init__(self, indent_size: int):
        self.lines: list[str] = []
        # Ensure nested structures remain distinguishable even for indent=0.
        normalized_indent = indent_size if indent_size > 0 else 1
        self.indentation_string = " " * normalized_indent
        self._indent_cache: dict[int, str] = {0: ""}
        self._indent_size = indent_size

    def push(self, depth: Depth, content: str):
        if depth not in self._indent_cache:
            if self._indent_size == 0:
                # indent=0 uses minimal spacing to preserve structure
                self._indent_cache[depth] = " " * depth
            else:
                self._indent_cache[depth] = self.indentation_string * depth
        indent = self._indent_cache[depth]
        self.lines.append(indent + content)

    def to_string(self) -> str:
        return "\n".join(self.lines)
