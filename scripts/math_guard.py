#!/usr/bin/env python3
"""SMPTeX: conservative, stdlib-only GitHub Markdown math preflight.

This is a source-level guard, NOT a MathJax parser or a browser-render guarantee.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import sys
from typing import Iterable

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\n]*)$")
ISOLATED_DISPLAY = re.compile(r"^\s*\$\$\s*$")
PROSE_TEX = re.compile(r"(?<!\\)\\(?:frac|sqrt|sum|prod|int|mathbb|mathcal|begin|operatorname|lim|left|right)\b")
BAD_DELIMITER = re.compile(r"(?<!\\)\\[\[(]")
UNSAFE = (
    "newcommand", "renewcommand", "providecommand", "usepackage",
    "includegraphics", "input", "require", "def",
)
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", ".tox", ".mypy_cache", ".pytest_cache", "dist", "build"}


@dataclass(frozen=True)
class Issue:
    path: str
    line: int
    code: str
    message: str


class Scanner:
    def __init__(self, path: str, strict_portable: bool = False, profile: str = "source"):
        if profile not in {"source", "repository-preview"}:
            raise ValueError(f"Unknown surface profile: {profile}")
        self.path = path
        self.strict_portable = strict_portable
        self.profile = profile
        self.issues: list[Issue] = []

    def error(self, line: int, code: str, message: str) -> None:
        self.issues.append(Issue(self.path, line, code, message))

    @staticmethod
    def escaped(s: str, pos: int) -> bool:
        k = pos - 1
        while k >= 0 and s[k] == "\\":
            k -= 1
        return ((pos - k - 1) % 2) == 1

    def math(self, tex: str, line: int, in_table: bool = False, context: str = "unknown") -> None:
        if not tex.strip():
            self.error(line, "EMPTY_MATH", "Empty math expression")
            return
        if in_table and any(ch == "|" and not self.escaped(tex, i) for i, ch in enumerate(tex)):
            self.error(line, "TABLE_PIPE", "Raw pipe inside table math may split Markdown cells; use \\mid, \\lvert/\\rvert, or move the equation outside the table")
        # TeX control words and control symbols consume their characters as a
        # unit. A pair of backslashes is a row break: the next brace
        # groups. An additional backslash instead makes that brace literal.
        stack: list[int] = []
        def at(pos: int) -> int:
            return line + tex.count("\n", 0, pos)

        commands: list[tuple[str, int]] = []
        i = 0
        while i < len(tex):
            ch = tex[i]
            if ch == "%":
                end = tex.find("\n", i)
                i = len(tex) if end < 0 else end + 1
                continue
            if ch == "\\":
                start = i
                i += 1
                if i == len(tex):
                    break
                if tex[i].isascii() and tex[i].isalpha():
                    while i < len(tex) and tex[i].isascii() and tex[i].isalpha():
                        i += 1
                else:
                    i += 1
                commands.append((tex[start + 1:i], start))
                continue
            if ch == "{":
                stack.append(i)
            elif ch == "}":
                if stack:
                    stack.pop()
                else:
                    self.error(at(i), "BRACES", "Unexpected closing brace in math")
            i += 1
        for pos in stack:
            self.error(at(pos), "BRACES", "Unclosed opening brace in math")

        env_stack: list[tuple[str, int]] = []
        delimiter_stack: list[int] = []
        for command, pos in commands:
            if self.profile == "repository-preview":
                if context in {"plain-inline", "dollar-display"} and command in {",", "{", "}"}:
                    self.error(at(pos), "REPO_PREVIEW_PUNCTUATION", f"Control symbol \\{command} corrupted a matched example in repository Preview in this delimiter context; inspect the target render or use protected inline / a math fence while preserving the TeX")
                elif context == "dollar-display" and command == "\\":
                    self.error(at(pos), "REPO_PREVIEW_ROW_SEPARATOR", "A matched matrix row separator failed in an isolated dollar display in repository Preview; inspect rows and columns or use a verified math fence")
            if command in {"begin", "end"}:
                match = re.match(r"\s*\{([A-Za-z][A-Za-z0-9*]*)\}", tex[pos + len(command) + 1:])
                if match:
                    name = match.group(1)
                    if command == "begin":
                        env_stack.append((name, pos))
                    elif not env_stack or env_stack[-1][0] != name:
                        self.error(at(pos), "ENVIRONMENT", f"Unmatched end of {name!r} environment")
                    else:
                        env_stack.pop()
                    if command == "begin" and name in {"tikzcd", "diagram", "picture"}:
                        self.error(at(pos), "UNSAFE_ENVIRONMENT", "Graphics/diagram LaTeX environments are not in the portable profile")
                else:
                    self.error(at(pos), "ENVIRONMENT", f"Missing or malformed environment name after \\{command}")
            if command == "left":
                delimiter_stack.append(pos)
            elif command == "right":
                if delimiter_stack:
                    delimiter_stack.pop()
                else:
                    self.error(at(pos), "LEFT_RIGHT", "Unexpected \\right before \\left")
            if command in UNSAFE:
                self.error(at(pos), "UNSAFE_MACRO", f"\\{command} is outside the portable authoring policy")
            if self.strict_portable and command == "operatorname":
                self.error(at(pos), "UNCERTIFIED_MACRO", "Use \\mathrm{...} instead of \\operatorname{...} (explicitly rejected on the observed GitHub repository-Markdown surface; other surfaces unverified)")
        for name, pos in env_stack:
            self.error(at(pos), "ENVIRONMENT", f"Unclosed environment: {name}")
        for pos in delimiter_stack:
            self.error(at(pos), "LEFT_RIGHT", "Unclosed \\left delimiter")

    @staticmethod
    def _blank(text: str, start: int, end: int) -> str:
        return text[:start] + " " * (end - start) + text[end:]

    def inline(self, line: str, number: int, in_table: bool = False, code_preprocessed: bool = False) -> None:
        # Official GitHub example wraps a literal currency dollar in a span.
        s = re.sub(r"<span>\$</span>", lambda m: " " * len(m.group(0)), line)
        prose = s
        i = 0
        while i < len(s):
            if s[i] == "`" and not code_preprocessed:
                n = len(s[i:]) - len(s[i:].lstrip("`"))
                marker = "`" * n
                end = s.find(marker, i + n)
                if end >= 0:
                    prose = self._blank(prose, i, end + n)
                    i = end + n
                    continue
                i += n
                continue
            if s[i] != "$" or self.escaped(s, i):
                i += 1
                continue
            if s.startswith("$$", i):
                self.error(number, "DISPLAY_DELIMITER", "Use $$ alone on its own lines for portable block math")
                prose = self._blank(prose, i, i + 2)
                i += 2
                continue
            if s.startswith("$`", i):
                end = s.find("`$", i + 2)
                if end < 0:
                    self.error(number, "UNTERMINATED_INLINE", "Missing closing backtick-dollar for $`...`$ math")
                    prose = self._blank(prose, i, len(s))
                    break
                self.math(s[i + 2:end], number, in_table=in_table, context="protected-inline")
                prose = self._blank(prose, i, end + 2)
                i = end + 2
                continue
            j = i + 1
            while j < len(s):
                if s[j] == "$" and not self.escaped(s, j):
                    break
                j += 1
            if j >= len(s):
                self.error(number, "UNTERMINATED_INLINE", "Unpaired $; for currency use an escaped dollar or GitHub's <span>$</span> form")
                prose = self._blank(prose, i, len(s))
                break
            self.math(s[i + 1:j], number, in_table=in_table, context="plain-inline")
            prose = self._blank(prose, i, j + 1)
            i = j + 1
        if BAD_DELIMITER.search(prose):
            self.error(number, "ALT_DELIMITER", "Use documented GitHub math delimiters ($...$, $`...`$, $$...$$, or ```math)")
        if PROSE_TEX.search(prose):
            self.error(number, "BARE_TEX", "TeX macro in prose outside math delimiters; wrap in inline code for literal examples")

    @staticmethod
    def _table_cells(line: str) -> list[str]:
        """Split GFM table cells at unescaped pipes (code spans do not protect pipes)."""
        parts, start = [], 0
        for i, ch in enumerate(line):
            if ch == "|" and not Scanner.escaped(line, i):
                parts.append(line[start:i])
                start = i + 1
        parts.append(line[start:])
        if len(parts) > 1 and not parts[0].strip():
            parts.pop(0)
        if len(parts) > 1 and not parts[-1].strip():
            parts.pop()
        return parts

    def _inline_block(self, records: list[tuple[int, str]]) -> None:
        if not records:
            return
        table_rows: set[int] = set()
        i = 1
        while i < len(records):
            header = records[i - 1][1]
            delim = records[i][1]
            cells = self._table_cells(delim)
            if ("|" in header or "|" in delim) and len(cells) == len(self._table_cells(header)) and all(re.fullmatch(r"\s*:?-+:?\s*", x) for x in cells):
                table_rows.add(i - 1)
                table_rows.add(i)
                j = i + 1
                while (j < len(records) and records[j][1].strip()
                       and not re.match(r" {0,3}(?:#{1,6}(?:\s|$)|>|(?:[-+*]|[0-9]{1,9}[.)])\s)", records[j][1])):
                    table_rows.add(j)
                    j += 1
                i = j
            else:
                i += 1
        def mask_code(joined: str) -> str:
            # Equal-length runs may span lines within the same paragraph or
            # cell, but never across cells, table rows, or block boundaries.
            masked = list(joined)
            i = 0
            while i < len(joined):
                if joined.startswith("$`", i) and not self.escaped(joined, i):
                    end = joined.find("`$", i + 2)
                    if end >= 0:
                        i = end + 2
                        continue
                if joined[i] != "`" or self.escaped(joined, i):
                    i += 1
                    continue
                n = 1
                while i + n < len(joined) and joined[i + n] == "`":
                    n += 1
                j = i + n
                close = -1
                while j < len(joined):
                    if joined[j] != "`":
                        j += 1
                        continue
                    k = j
                    while k < len(joined) and joined[k] == "`":
                        k += 1
                    if k - j == n:
                        close = k
                        break
                    j = k
                if close < 0:
                    i += n
                    continue
                for k in range(i, close):
                    if masked[k] != "\n":
                        masked[k] = " "
                i = close
            return "".join(masked)

        lines = [text for _, text in records]
        i = 0
        while i < len(lines):
            if i in table_rows:
                row = lines[i]
                # Preserve delimiters for TABLE_PIPE while preventing code
                # spans from consuming text in a different cell.
                cuts = [j for j, ch in enumerate(row) if ch == "|" and not self.escaped(row, j)]
                pieces, start = [], 0
                for cut in cuts:
                    pieces.extend((mask_code(row[start:cut]), "|"))
                    start = cut + 1
                pieces.append(mask_code(row[start:]))
                lines[i] = "".join(pieces)
                i += 1
            else:
                j = i + 1
                while j < len(lines) and j not in table_rows:
                    j += 1
                lines[i:j] = mask_code("\n".join(lines[i:j])).split("\n")
                i = j
        for i, ((number, _), text) in enumerate(zip(records, lines)):
            self.inline(text, number, in_table=i in table_rows, code_preprocessed=True)

    @staticmethod
    def _blank_container_line(line: str) -> bool:
        return not re.sub(r"^(?: {0,3}> ?)+", "", line).strip()

    def scan(self, content: str) -> list[Issue]:
        fence_char = ""
        fence_len = 0
        is_math_fence = False
        math_lines: list[str] = []
        math_start = 0
        display = False
        display_lines: list[str] = []
        display_start = 0
        records: list[tuple[int, str]] = []
        comment = False
        comment_quote = comment_list = 0
        list_indent = 0
        fence_quote = fence_list = 0
        display_quote = display_list = 0
        code_marker = ""
        record_quote = 0
        raw_lines = content.splitlines()
        for number, raw in enumerate(raw_lines, 1):
            # Explicit block-quote prefixes, then a simple list marker or its
            # content indent. Complex lazy/nested lists are not fully parsed.
            quote_match = re.match(r"^(?: {0,3}> ?)+", raw)
            quote_prefix = quote_match.group(0) if quote_match else ""
            quote_depth = quote_prefix.count(">")
            line = raw[len(quote_prefix):]
            if fence_char and (quote_depth < fence_quote or (fence_list and line.strip() and not line.startswith(" " * fence_list))):
                if is_math_fence:
                    self.math("\n".join(math_lines), math_start + 1, context="math-fence")
                self.error(math_start if is_math_fence else number - 1, "UNTERMINATED_FENCE", "Unclosed Markdown code fence at container boundary")
                fence_char = ""
                is_math_fence = False
                math_lines = []
            if comment and (quote_depth < comment_quote or (comment_list and line.strip() and not line.startswith(" " * comment_list))):
                comment = False
            if display and (quote_depth < display_quote or (display_list and line.strip() and not line.startswith(" " * display_list))):
                self.math("\n".join(display_lines), display_start + 1, context="dollar-display")
                self.error(display_start, "UNTERMINATED_DISPLAY", "Missing closing $$ before container boundary")
                display = False
                display_lines = []
            marker = re.match(r"^ {0,3}(?:[-+*]|[0-9]{1,9}[.)])[ \t]+", line)
            if not fence_char and not display and records and (quote_depth != record_quote or marker):
                self._inline_block(records)
                records = []
                code_marker = ""
            record_quote = quote_depth
            if marker:
                list_indent = len(marker.group(0))
                line = line[list_indent:]
            elif list_indent and line.startswith(" " * list_indent):
                line = line[list_indent:]
            elif line.strip():
                list_indent = 0
            if list_indent and re.match(r"^ {0,3}>", line):
                self.error(number, "UNSUPPORTED_CONTAINER", "A block quote inside a list is outside the scanner's supported Markdown subset; inspect it separately")

            fence = FENCE.match(line)
            if fence_char:
                if (fence and fence.group(1)[0] == fence_char
                        and len(fence.group(1)) >= fence_len
                        and not fence.group(2).strip()):
                    if is_math_fence:
                        self.math("\n".join(math_lines), math_start + 1, context="math-fence")
                    fence_char = ""
                    is_math_fence = False
                    math_lines = []
                elif is_math_fence:
                    math_lines.append(line)
                continue
            if display:
                if ISOLATED_DISPLAY.match(line):
                    self.math("\n".join(display_lines), display_start + 1, context="dollar-display")
                    if self.profile == "repository-preview" and number < len(raw_lines) and not self._blank_container_line(raw_lines[number]):
                        self.error(number, "REPO_PREVIEW_DISPLAY_BOUNDARY", "An adjacent-prose challenge rendered literal delimiters in repository Preview; separate the display with blank lines and inspect the target")
                    display = False
                    display_lines = []
                else:
                    if self.profile == "repository-preview":
                        display_source = raw
                        for _ in range(display_quote):
                            display_source = re.sub(r"^ {0,3}> ?", "", display_source, count=1)
                        if display_list and display_source.startswith(" " * display_list):
                            display_source = display_source[display_list:]
                        if re.match(r"^ {0,3}(?:=+[ \t]*$|(?:-[ \t]*){3,}$|(?:[-+*]|[0-9]{1,9}[.)])[ \t]+|>[ \t]?|#{1,6}(?:[ \t]|$))", display_source):
                            self.error(number, "REPO_PREVIEW_DISPLAY_BLOCK", "A Markdown-active line in a dollar display split a repository Preview challenge; inspect the source and consider a math fence (this check does not establish TeX validity)")
                    display_lines.append(line)
                continue
            # Comments are not recognized within same-line code or math.
            chars = list(line)
            i = 0
            while i < len(line):
                if comment:
                    end = line.find("-->", i)
                    stop = len(line) if end < 0 else end + 3
                    chars[i:stop] = " " * (stop - i)
                    i = stop
                    if end >= 0:
                        comment = False
                    continue
                if code_marker:
                    match = re.search(r"(?<!`)" + re.escape(code_marker) + r"(?!`)", line[i:])
                    if match:
                        i += match.end()
                        code_marker = ""
                    else:
                        i = len(line)
                    continue
                if line.startswith("<!--", i):
                    comment_quote, comment_list = quote_depth, list_indent
                    comment = True
                    continue
                if line[i] == "$" and not self.escaped(line, i):
                    if line.startswith("$`", i):
                        end = line.find("`$", i + 2)
                        if end >= 0:
                            i = end + 2
                            continue
                    else:
                        end = i + 1
                        while end < len(line) and (line[end] != "$" or self.escaped(line, end)):
                            end += 1
                        if end < len(line):
                            i = end + 1
                            continue
                if line[i] == "`" and not self.escaped(line, i):
                    match = re.match(r"`+", line[i:])
                    marker = match.group(0)
                    close = re.search(r"(?<!`)" + re.escape(marker) + r"(?!`)", line[i + len(marker):])
                    if close:
                        i += len(marker) + close.end()
                        continue
                    # Only treat an unmatched opener as a multiline code span
                    # if an exact closer exists before a block boundary.
                    closer = re.compile(r"(?<!`)" + re.escape(marker) + r"(?!`)")
                    for future in raw_lines[number:]:
                        plain = re.sub(r"^(?: {0,3}> ?)+", "", future)
                        if not plain.strip() or FENCE.match(plain):
                            break
                        if closer.search(plain):
                            code_marker = marker
                            break
                    i += len(marker)
                    continue
                i += 1
            line = "".join(chars)
            if re.match(r"^ {0,3}(?:</?(?:address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|pre|script|search|section|source|style|summary|table|tbody|td|textarea|tfoot|th|thead|title|tr|track|ul)(?=[\s/>]|$)|<\?|<![A-Z]|<!\[CDATA\[)", line, re.IGNORECASE) or re.match(r"^ {0,3}</?[A-Za-z][A-Za-z0-9-]*(?:[ \t]+.*)?[ \t]*/?>[ \t]*$", line):
                self.error(number, "UNSUPPORTED_HTML_BLOCK", "HTML blocks other than comments require separate inspection")
            fence = FENCE.match(line)
            if fence and fence.group(1)[0] == "`" and "`" in fence.group(2):
                fence = None
            if fence:
                self._inline_block(records)
                records = []
                fence_char = fence.group(1)[0]
                fence_quote, fence_list = quote_depth, list_indent
                fence_len = len(fence.group(1))
                language = fence.group(2).strip().split(maxsplit=1)[0].lower() if fence.group(2).strip() else ""
                is_math_fence = language == "math"
                if is_math_fence:
                    math_start = number
                    math_lines = []
                continue
            if (line.startswith("    ") or line.startswith("\t")) and not records:
                continue
            if ISOLATED_DISPLAY.match(line):
                self._inline_block(records)
                records = []
                display = True
                display_quote, display_list = quote_depth, list_indent
                if self.profile == "repository-preview":
                    if display_list:
                        self.error(number, "REPO_PREVIEW_LIST_DISPLAY", "A list-contained dollar display rendered as literal text in repository Preview; inspect this list and consider a math fence")
                    if number > 1 and not self._blank_container_line(raw_lines[number - 2]):
                        self.error(number, "REPO_PREVIEW_DISPLAY_BOUNDARY", "An adjacent-prose challenge rendered literal delimiters in repository Preview; separate the display with blank lines and inspect the target")
                display_start = number
                display_lines = []
                continue
            block_boundary = re.match(r"^ {0,3}(?:#{1,6}(?:[ \t]|$)|(?:=+|-+)[ \t]*$|(?:[*_-][ \t]*){3,}$)", line)
            if block_boundary:
                self._inline_block(records)
                records = []
                code_marker = ""
                self.inline(line, number)
            elif not line.strip():
                self._inline_block(records)
                records = []
                code_marker = ""
            else:
                records.append((number, line))
        self._inline_block(records)
        eof = len(content.splitlines()) or 1
        if display:
            self.math("\n".join(display_lines), display_start + 1, context="dollar-display")
            self.error(display_start, "UNTERMINATED_DISPLAY", "Missing closing $$ on its own line")
        if fence_char:
            if is_math_fence:
                self.math("\n".join(math_lines), math_start + 1, context="math-fence")
            self.error(math_start if is_math_fence else eof, "UNTERMINATED_FENCE", "Unclosed Markdown code fence")
        return self.issues


def all_markdown(paths: Iterable[str]) -> list[Path]:
    results: set[Path] = set()
    for raw in paths:
        p = Path(raw)
        if not p.exists():
            raise FileNotFoundError(str(p))
        if p.is_file():
            results.add(p)
        else:
            for root, dirs, filenames in os.walk(p):
                dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
                for filename in filenames:
                    file = Path(root) / filename
                    if file.suffix.lower() in {".md", ".markdown", ".mdown"}:
                        results.add(file)
    return sorted(results)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("paths", nargs="*", default=["."], help="Markdown files or directories to scan")
    p.add_argument("--strict-portable", action="store_true", help="Disallow uncertified macros such as operatorname")
    p.add_argument("--json", action="store_true", help="Emit machine-readable findings")
    p.add_argument("--profile", choices=("source", "repository-preview"), default="source", help="Surface-specific observations to check; source is the default")
    p.add_argument("--exclude", action="append", default=[], metavar="PATH", help="Exclude an exact repository-relative Markdown path (must be checked separately)")
    args = p.parse_args(argv)
    try:
        paths = all_markdown(args.paths)
    except (FileNotFoundError, PermissionError) as exc:
        print(f"math_guard: path error: {exc}", file=sys.stderr)
        return 2
    excluded = {Path(value).as_posix().removeprefix("./") for value in args.exclude}
    results: list[Issue] = []
    scanned = 0
    for path in paths:
        try:
            relative = path.resolve().relative_to(Path.cwd().resolve()).as_posix()
        except ValueError:
            relative = path.as_posix()
        if relative in excluded:
            continue
        scanned += 1
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError) as exc:
            results.append(Issue(str(path), 1, "READ_ERROR", str(exc)))
            continue
        results.extend(Scanner(str(path), args.strict_portable, profile=args.profile).scan(content))
    if args.json:
        print(json.dumps({"profile": args.profile, "scanned": scanned, "issues": [asdict(x) for x in results]}, indent=2))
    else:
        for issue in results:
            print(f"{issue.path}:{issue.line}: {issue.code}: {issue.message}")
        print(f"SMPTeX: {scanned} Markdown file(s) scanned; {len(results)} issue(s)")
    return 1 if results else 0


if __name__ == "__main__":
    raise SystemExit(main())
