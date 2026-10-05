# ABOUTME: Parses the small YAML subset the metacognition formats use, stdlib only.
# ABOUTME: Anything outside the documented subset raises an error naming the line.
"""Parse the small YAML subset the metacognition formats use. Standard library only.

Input is frontmatter text (without the "---" delimiters) or a whole config file.
Output is a dict, or a raised YamlSubsetError (a ValueError) whose message starts with
"line N:", the 1-indexed line of the offending construct.

Supported constructs, and nothing else:

* "key: value" pairs, one per line. Keys are bare or quoted strings.
* Strings, bare or quoted. Double quotes allow the escapes \\\\, \\", \\n, and \\t.
  Single quotes allow '' for a literal single quote.
* Integers such as 3, -2, or +7 (decimal, no leading zeros).
* Bare ISO dates, YYYY-MM-DD, which parse to datetime.date as PyYAML does. Quote one to keep a string.
* The literals true, false, and null, in lowercase.
* Inline lists: [a, b, "c"].
* Inline maps: {k: v, other: 2}.
* Inline lists and maps nested in each other, such as [{a: 1}, {b: [x, y]}]. Each stays on one line.
* Block maps by indentation, spaces only. A "key:" with nothing after it and no deeper lines is null.
* "#" comments, on their own line or after a value (the "#" must follow whitespace).
* One optional leading "---" line.

Anything else is an error, never a guess. That covers anchors (&a), aliases (*a), tags (!!str),
a "---" or "..." after the first content line, block scalars (| and >), block sequences ("- item"),
floats, timestamps (a date with a time), non-ISO or impossible dates, and the YAML 1.1 spellings
that PyYAML would read as another type (True, Null, ~, yes, no, on, off), duplicate keys, tabs in
indentation, and indentation that does not match an open block.

Run as a script, it prints the parsed result as JSON:

    python3 scripts/yaml_subset.py <file>
"""

import datetime
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

type YamlValue = str | int | bool | datetime.date | None | list[YamlValue] | dict[str, YamlValue]
type YamlMap = dict[str, YamlValue]

_INDICATOR_ERRORS = {
    "&": "anchors are not supported",
    "*": "aliases are not supported",
    "!": "tags are not supported",
    "|": "block scalars are not supported",
    ">": "block scalars are not supported",
    "%": "directives are not supported",
    "@": "reserved indicator '@' is not supported",
    "`": "reserved indicator '`' is not supported",
    "?": "complex keys are not supported",
}
_INT = re.compile(r"[+-]?(0|[1-9][0-9]*)")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_NUMBER_LIKE = re.compile(
    r"[+-]?(\d[\d_]*\.?\d*|\.\d+)([eE][+-]?\d+)?|[+-]?\d+(:[0-5]?\d)+|\d{4}-\d{1,2}-\d{1,2}.*|[+-]?\.(inf|nan)",
    re.IGNORECASE,
)
_YAML11_WORDS = {"~", "yes", "no", "on", "off", "true", "false", "null"}
_ESCAPES = {"\\": "\\", '"': '"', "n": "\n", "t": "\t"}
_KEY_SEPARATOR = re.compile(r":(?:\s|$)")


class YamlSubsetError(ValueError):
    """Raised for any construct outside the supported subset."""

    def __init__(self, lineno: int, message: str) -> None:
        super().__init__(f"line {lineno}: {message}")


@dataclass(frozen=True)
class _Line:
    lineno: int
    indent: int
    text: str


def _is_quote_start(text: str, index: int) -> bool:
    return index == 0 or text[index - 1] in " \t[{,:"


def _strip_comment(text: str) -> str:
    """Drop a trailing "#" comment, ignoring "#" inside quotes."""
    quote = ""
    index = 0
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\" and quote == '"':
                index += 1
            elif char == quote:
                if quote == "'" and text[index + 1 : index + 2] == "'":
                    index += 1
                else:
                    quote = ""
        elif char in "\"'" and _is_quote_start(text, index):
            quote = char
        elif char == "#" and (index == 0 or text[index - 1] in " \t"):
            return text[:index]
        index += 1
    return text


def _tokenize(text: str) -> list[_Line]:
    lines: list[_Line] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        content = _strip_comment(raw).rstrip()
        if not content.strip():
            continue
        stripped = content.lstrip(" ")
        indent = len(content) - len(stripped)
        if stripped[0] == "\t":
            raise YamlSubsetError(lineno, "tabs are not allowed in indentation")
        if stripped == "---" or stripped.startswith("--- "):
            if lines:
                raise YamlSubsetError(lineno, "multi-document streams are not supported")
            continue
        if stripped == "..." or stripped.startswith("... "):
            raise YamlSubsetError(lineno, "multi-document streams are not supported")
        lines.append(_Line(lineno, indent, stripped))
    return lines


def _read_quoted(text: str, start: int, lineno: int) -> tuple[str, int]:
    """Read a quoted string starting at text[start]. Return the value and the index after it."""
    quote = text[start]
    chars: list[str] = []
    index = start + 1
    while index < len(text):
        char = text[index]
        if quote == '"' and char == "\\":
            escape = text[index + 1] if index + 1 < len(text) else ""
            if escape not in _ESCAPES:
                raise YamlSubsetError(lineno, f"unsupported escape sequence '\\{escape}'")
            chars.append(_ESCAPES[escape])
            index += 2
        elif char == quote:
            if quote == "'" and text[index + 1 : index + 2] == "'":
                chars.append("'")
                index += 2
            else:
                return "".join(chars), index + 1
        else:
            chars.append(char)
            index += 1
    raise YamlSubsetError(lineno, "unterminated quoted string")


def _coerce_bare(text: str, lineno: int) -> str | int | bool | datetime.date | None:
    """Turn a bare scalar into a str, int, bool, date, or None, or raise if its type is ambiguous."""
    if not text:
        raise YamlSubsetError(lineno, "empty value")
    if text[0] in _INDICATOR_ERRORS:
        raise YamlSubsetError(lineno, _INDICATOR_ERRORS[text[0]])
    if text == "-" or text.startswith("- "):
        raise YamlSubsetError(lineno, "block sequences are not supported")
    if text[0] in "[{":
        raise YamlSubsetError(lineno, "unbalanced inline collection")
    if text == "true":
        return True
    if text == "false":
        return False
    if text == "null":
        return None
    if text.lower() in _YAML11_WORDS:
        raise YamlSubsetError(lineno, f"ambiguous scalar '{text}'; quote it, or use true, false, or null")
    if _INT.fullmatch(text):
        return int(text)
    if _ISO_DATE.fullmatch(text):
        try:
            return datetime.date.fromisoformat(text)
        except ValueError:
            raise YamlSubsetError(lineno, f"invalid calendar date '{text}'") from None
    if _NUMBER_LIKE.fullmatch(text):
        raise YamlSubsetError(lineno, f"ambiguous number-like scalar '{text}'; only plain integers are supported")
    return text


class _FlowReader:
    """Recursive-descent reader for one-line inline lists and maps."""

    def __init__(self, text: str, lineno: int) -> None:
        self.text = text
        self.lineno = lineno
        self.pos = 0

    def read_document(self) -> YamlValue:
        value = self.read_value()
        self.skip_space()
        if self.pos != len(self.text):
            raise YamlSubsetError(self.lineno, f"unexpected text after value: '{self.text[self.pos :]}'")
        return value

    def skip_space(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos] in " \t":
            self.pos += 1

    def peek(self) -> str:
        self.skip_space()
        return self.text[self.pos] if self.pos < len(self.text) else ""

    def read_value(self) -> YamlValue:
        char = self.peek()
        if char == "[":
            return self.read_list()
        if char == "{":
            return self.read_map()
        if char in ("'", '"'):
            value, self.pos = _read_quoted(self.text, self.pos, self.lineno)
            return value
        return _coerce_bare(self.read_bare(",]}"), self.lineno)

    def read_bare(self, stops: str) -> str:
        start = self.pos
        while self.pos < len(self.text):
            if self.text[self.pos] in stops:
                break
            if self.text[self.pos] == ":" and self.text[self.pos + 1 : self.pos + 2] in ("", " "):
                raise YamlSubsetError(self.lineno, "unexpected ':' in a scalar")
            self.pos += 1
        return self.text[start : self.pos].strip()

    def read_list(self) -> list[YamlValue]:
        items: list[YamlValue] = []
        self.pos += 1
        if self.peek() == "]":
            self.pos += 1
            return items
        while True:
            items.append(self.read_value())
            char = self.peek()
            self.pos += 1
            if char == "]":
                return items
            if char != ",":
                raise YamlSubsetError(self.lineno, "expected ',' or ']' in inline list")

    def read_map(self) -> YamlMap:
        mapping: YamlMap = {}
        self.pos += 1
        if self.peek() == "}":
            self.pos += 1
            return mapping
        while True:
            key = self.read_key()
            if key in mapping:
                raise YamlSubsetError(self.lineno, f"duplicate key '{key}'")
            mapping[key] = self.read_value()
            char = self.peek()
            self.pos += 1
            if char == "}":
                return mapping
            if char != ",":
                raise YamlSubsetError(self.lineno, "expected ',' or '}' in inline map")

    def read_key(self) -> str:
        if self.peek() in ("'", '"'):
            key, self.pos = _read_quoted(self.text, self.pos, self.lineno)
        else:
            start = self.pos
            while self.pos < len(self.text) and self.text[self.pos] not in ",{}[]":
                if self.text[self.pos] == ":" and self.text[self.pos + 1 : self.pos + 2] in ("", " "):
                    break
                self.pos += 1
            key = _bare_key(self.text[start : self.pos].strip(), self.lineno)
        if self.peek() != ":":
            raise YamlSubsetError(self.lineno, "expected ':' after key in inline map")
        self.pos += 1
        return key


def _bare_key(text: str, lineno: int) -> str:
    key = _coerce_bare(text, lineno)
    if not isinstance(key, str):
        raise YamlSubsetError(lineno, f"ambiguous key '{text}'; quote it")
    return key


def _parse_value(text: str, lineno: int) -> YamlValue:
    if text[0] in "[{":
        return _FlowReader(text, lineno).read_document()
    if text[0] in "\"'":
        value, end = _read_quoted(text, 0, lineno)
        if text[end:].strip():
            raise YamlSubsetError(lineno, f"unexpected text after quoted string: '{text[end:].strip()}'")
        return value
    if _KEY_SEPARATOR.search(text):
        raise YamlSubsetError(lineno, "nested mapping on the same line is not supported")
    return _coerce_bare(text, lineno)


def _split_key(line: _Line) -> tuple[str, str]:
    text = line.text
    if text[0] in "\"'":
        key, end = _read_quoted(text, 0, line.lineno)
        rest = text[end:].lstrip(" ")
        if not rest.startswith(":") or rest[1:2] not in ("", " "):
            raise YamlSubsetError(line.lineno, "expected 'key: value'")
        return key, rest[1:].strip()
    if text == "-" or text.startswith("- "):
        raise YamlSubsetError(line.lineno, "block sequences are not supported")
    separator = _KEY_SEPARATOR.search(text)
    if separator is None:
        raise YamlSubsetError(line.lineno, "expected 'key: value'")
    key = _bare_key(text[: separator.start()].strip(), line.lineno)
    return key, text[separator.end() :].strip()


def _parse_block(lines: list[_Line], start: int, indent: int) -> tuple[YamlMap, int]:
    """Parse the block map whose keys sit at `indent`. Return it and the index of the next unread line."""
    mapping: YamlMap = {}
    pos = start
    while pos < len(lines) and lines[pos].indent >= indent:
        line = lines[pos]
        if line.indent > indent:
            raise YamlSubsetError(line.lineno, "unexpected indentation")
        key, rest = _split_key(line)
        if key in mapping:
            raise YamlSubsetError(line.lineno, f"duplicate key '{key}'")
        pos += 1
        if rest:
            mapping[key] = _parse_value(rest, line.lineno)
        elif pos < len(lines) and lines[pos].indent > indent:
            mapping[key], pos = _parse_block(lines, pos, lines[pos].indent)
        else:
            mapping[key] = None
    return mapping, pos


def extract_frontmatter(text: str) -> str | None:
    """Return the frontmatter of a markdown file, without the "---" delimiters.

    The block must start on the first line with "---" and end at the next line that is exactly "---".

    Args:
        text: The whole markdown file.

    Returns:
        The text between the two delimiter lines (empty string for an empty block), or None when
        the file has no complete frontmatter block.
    """
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            return "\n".join(lines[1:index])
    return None


def parse(text: str) -> YamlMap:
    """Parse YAML-subset text into a dict.

    Args:
        text: Frontmatter text or a whole config file.

    Returns:
        The parsed top-level mapping. Empty or comment-only input gives {}.

    Raises:
        YamlSubsetError: On any construct outside the subset. The message names the 1-indexed line.
    """
    lines = _tokenize(text)
    if not lines:
        return {}
    if lines[0].indent != 0:
        raise YamlSubsetError(lines[0].lineno, "unexpected indentation")
    mapping, pos = _parse_block(lines, 0, 0)
    if pos < len(lines):
        raise YamlSubsetError(lines[pos].lineno, "unexpected indentation")
    return mapping


def _json_default(value: object) -> str:
    """Serialize the one non-JSON type the parser returns, datetime.date, as an ISO string."""
    if isinstance(value, datetime.date):
        return value.isoformat()
    raise TypeError(f"cannot serialize {type(value).__name__}")


def main(argv: list[str]) -> int:
    """Parse the file named in argv[1] and print the result as JSON."""
    if len(argv) != 2:
        print("usage: yaml_subset.py <file>", file=sys.stderr)
        return 2
    try:
        result = parse(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"{argv[1]}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, default=_json_default))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
