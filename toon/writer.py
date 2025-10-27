from .types import Depth

class LineWriter:
    def __init__(self, indent_size: int):
        self.lines: list[str] = []
        self.indentation_string = ' ' * indent_size

    def push(self, depth: Depth, content: str):
        indent = self.indentation_string * depth
        self.lines.append(indent + content)

    def to_string(self) -> str:
        return '\n'.join(self.lines)
