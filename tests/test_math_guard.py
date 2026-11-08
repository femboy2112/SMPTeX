"""Mutation controls: known-valid documents pass; deliberately broken ones fail."""
import importlib.util
from pathlib import Path
import tempfile
import os
import subprocess
import json
import io
from contextlib import redirect_stdout
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "math_guard.py"
spec = importlib.util.spec_from_file_location("math_guard", MODULE)
import sys
math_guard = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = math_guard
spec.loader.exec_module(math_guard)


def errors(src: str, strict: bool = True):
    return math_guard.Scanner("fixture.md", strict).scan(src)


class MathGuardTests(unittest.TestCase):
    def test_repository_preview_profile_is_delimiter_sensitive(self):
        spacing = r"\int_0^1 x^2\,dx=\frac13"
        braces = r"\{x\in X\mid P(x)\}\subseteq X"
        matrix = r"\begin{pmatrix}a&b\\c&d\end{pmatrix}"
        for expression in (spacing, braces):
            for source in ("$" + expression + "$", "$$\n" + expression + "\n$$"):
                with self.subTest(source=source):
                    self.assertEqual(errors(source), [])
                    found = math_guard.Scanner("fixture.md", True, profile="repository-preview").scan(source)
                    self.assertTrue(any(e.code == "REPO_PREVIEW_PUNCTUATION" for e in found))
            for source in ("$`" + expression + "`$", "```math\n" + expression + "\n```"):
                self.assertEqual(math_guard.Scanner("fixture.md", True, profile="repository-preview").scan(source), [])
        row_display = "$$\n" + matrix + "\n$$"
        self.assertTrue(any(e.code == "REPO_PREVIEW_ROW_SEPARATOR" for e in math_guard.Scanner("fixture.md", True, profile="repository-preview").scan(row_display)))
        self.assertEqual(math_guard.Scanner("fixture.md", True, profile="repository-preview").scan("```math\n" + matrix + "\n```"), [])
        # The row break consumes both slashes; the subsequent comma is not a
        # thin-space control symbol. No punctuation finding should be invented.
        slash_pair = "```math\n" + "\\" * 2 + ",x\n```"
        self.assertEqual(math_guard.Scanner("fixture.md", True, profile="repository-preview").scan(slash_pair), [])

    def test_repository_preview_display_context_controls(self):
        def findings(src):
            return math_guard.Scanner("fixture.md", True, profile="repository-preview").scan(src)
        positive = ("$$\nx=y\n$$", "  $$\n  x=y\n  $$", "> Quote.\n>\n> $$\n> x=y\n> $$\n>\n> Continuation.", "```math\nA\n=\nB\n```")
        for source in positive:
            with self.subTest(source=source):
                self.assertEqual(findings(source), [])
        adjacent = "Text\n$$\na=b\n$$\nText"
        boundary = [e.line for e in findings(adjacent) if e.code == "REPO_PREVIEW_DISPLAY_BOUNDARY"]
        self.assertEqual(boundary, [2, 4])
        for token in ("=", "---", "- B", "> B", "# B"):
            source = "$$\nA\n" + token + "\nB\n$$"
            self.assertTrue(any(e.code == "REPO_PREVIEW_DISPLAY_BLOCK" and e.line == 3 for e in findings(source)), token)
            self.assertFalse(any(e.code.startswith("REPO_PREVIEW_") for e in errors(source)))
        for token in ("***", "___"):
            self.assertFalse(any(e.code == "REPO_PREVIEW_DISPLAY_BLOCK" for e in findings("$$\nA\n" + token + "\nB\n$$")))
        list_src = "- List item.\n\n  $$\n  x=y\n  $$\n\n  Continuation."
        self.assertTrue(any(e.code == "REPO_PREVIEW_LIST_DISPLAY" and e.line == 3 for e in findings(list_src)))

    def test_profile_cli_json_default_and_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profile.md"
            path.write_text(r"$x\,y$", encoding="utf8")
            for extra, label, expected in (([], "source", 0), (["--profile", "repository-preview"], "repository-preview", 1)):
                run = subprocess.run([sys.executable, str(MODULE), str(path), "--json", *extra], capture_output=True, text=True)
                self.assertEqual(run.returncode, expected)
                result = json.loads(run.stdout)
                self.assertEqual(result["profile"], label)
                self.assertEqual(any(e["code"] == "REPO_PREVIEW_PUNCTUATION" for e in result["issues"]), bool(expected))
            bad = subprocess.run([sys.executable, str(MODULE), str(path), "--profile", "wiki"], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)

    def test_exclude_specific_probe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ordinary.md").write_text(r"$\operatorname{rank}(A)$", encoding="utf8")
            (root / "probe.md").write_text(r"$\operatorname{rank}(A)$", encoding="utf8")
            orig = Path.cwd()
            os.chdir(root)
            try:
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(math_guard.main([".", "--strict-portable", "--exclude", "probe.md"]), 1)
                    self.assertEqual(math_guard.main(["probe.md"]), 0)
            finally:
                os.chdir(orig)

    def test_exclude_exact_not_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "probe.md").write_text(r"$\operatorname{rank}(A)$", encoding="utf8")
            orig = Path.cwd()
            os.chdir(root)
            try:
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(math_guard.main([".", "--strict-portable", "--exclude", "probe.md.extra"]), 1)
                    self.assertEqual(math_guard.main([".", "--strict-portable", "--exclude", "probe.md"]), 0)
            finally:
                os.chdir(orig)

    def test_control_symbols_brace_parity_scanner_and_cli(self):
        def fenced(body):
            return "```math\n" + body + "\n```\n"

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "parity.md"
            for n in range(1, 5):
                slash = "\\" * n
                for brace in "{}":
                    # For odd runs the target brace is literal. For even runs
                    # supply its matching group delimiter elsewhere.
                    valid = (slash + "{x" if n % 2 else slash + "{x}") if brace == "{" else ("x" + slash + "}" if n % 2 else "{x" + slash + "}")
                    broken = valid + ("}" if n % 2 else "") if brace == "{" else ("{" + valid if n % 2 else valid[1:])
                    if brace == "{" and n % 2 == 0:
                        broken = valid[:-1]
                    for src, expected in ((valid, False), (broken, True)):
                        with self.subTest(n=n, brace=brace, src=src):
                            body = fenced(src)
                            direct = errors(body)
                            self.assertEqual(any(e.code == "BRACES" for e in direct), expected)
                            path.write_text(body, encoding="utf8")
                            run = subprocess.run([sys.executable, str(MODULE), str(path), "--json"], capture_output=True, text=True)
                            self.assertEqual(run.returncode, int(expected), run.stderr)
                            result = json.loads(run.stdout)
                            self.assertEqual(any(e["code"] == "BRACES" for e in result["issues"]), expected)

    def test_row_break_followed_by_group(self):
        prefix = r"\begin{aligned} a&=b" + "\\" * 2
        suffix = r" \end{aligned}"
        self.assertEqual(errors("```math\n" + prefix + "{x}" + suffix + "\n```"), [])
        self.assertTrue(any(e.code == "BRACES" for e in errors("```math\n" + prefix + "{x" + suffix + "\n```")))
        self.assertEqual(errors("```math\n" + prefix + r"\{x" + suffix + "\n```"), [])

    def test_ordered_delimiters_and_escaped_commands(self):
        for body, code in ((r"\right) x \left(", "LEFT_RIGHT"),
                           (r"\end{aligned}\begin{aligned}", "ENVIRONMENT")):
            self.assertTrue(any(e.code == code for e in errors("```math\n" + body + "\n```")))
        self.assertEqual(errors("```math\n" + r"\\begin{aligned} \\left( \\operatorname{x}" + "\n```"), [])

    def test_environment_whitespace_and_malformed_names(self):
        for tex, code in ((r"\begin {tikzcd} x \end {tikzcd}", "UNSAFE_ENVIRONMENT"),
                          (r"\begin {aligned} x \end {matrix}", "ENVIRONMENT"),
                          (r"\begin x", "ENVIRONMENT")):
            self.assertTrue(any(e.code == code for e in errors("```math\n" + tex + "\n```")))
        self.assertEqual(errors("```math\n" + r"\begin {aligned}x\end {aligned}" + "\n```"), [])

    def test_math_comment_and_diagnostic_lines(self):
        src = "```math\n" + r"x % { \newcommand{foo}" + "\n" + r"\frac{1}{x" + "\n```"
        findings = errors(src)
        self.assertEqual([(e.code, e.line) for e in findings], [("BRACES", 3)])
        self.assertTrue(any(e.code == "UNSAFE_MACRO" and e.line == 3 for e in errors("```math\nx\n" + r"\newcommand{a}{b}" + "\n```")))
        self.assertTrue(any(e.code == "BRACES" for e in errors("```math\n" + r"\% {" + "\n```")))

    def test_table_context_and_pipe_locations(self):
        for src in ("a | b\n--- | ---\nA | $|x|$", "| a | b |\n| --- | --- |\n| A | $|x|$ |"):
            self.assertEqual([(e.code, e.line) for e in errors(src)], [("TABLE_PIPE", 3)])
        self.assertEqual(errors("| ordinary prose $|x|$"), [])
        self.assertEqual(errors("a | b\n--- | ---\n# heading $|x|$"), [])
        self.assertEqual(errors("a | b\n--- | ---\nA | $x\\|y$"), [])
        self.assertEqual(errors("a | b\n--- | --- | ---\nA | $|x|$"), [])

    def test_literal_contexts_and_live_controls(self):
        literals = ("    $\\newcommand{x}{y}$", "`example\n$\\newcommand{x}{y}$`", "<!--\n$\\newcommand{x}{y}$\n-->", "```text\n$\\newcommand{x}{y}$\n```")
        for literal in literals:
            with self.subTest(literal=literal):
                self.assertEqual(errors(literal), [])
                self.assertTrue(any(e.code == "UNSAFE_MACRO" for e in errors("```math\n\\newcommand{x}{y}\n```")))
        self.assertTrue(any(e.code == "UNSAFE_MACRO" for e in errors("paragraph\n    $\\newcommand{x}{y}$")))
        self.assertTrue(any(e.code == "UNSAFE_MACRO" for e in errors("`<!--` $\\newcommand{x}{y}$")))

    def test_unsupported_html_block_does_not_pass_silently(self):
        src = "<div>\n```text\n</div>\n$\\operatorname{x}$"
        self.assertTrue(any(e.code == "UNSUPPORTED_HTML_BLOCK" for e in errors(src)))
        for tag in ("<custom-tag>", '<custom-tag data-x="a">', '<custom-tag data-x=">">', "<script", "<div"):
            src = tag + "\n```\nhtml content\n\n$\\operatorname{x}$\n```"
            self.assertTrue(any(e.code == "UNSUPPORTED_HTML_BLOCK" for e in errors(src)), tag)
        self.assertEqual(errors("Text <span>inline</span> $x$"), [])

    def test_comments_end_at_container_boundaries(self):
        for text in ("> <!--\n$\\operatorname{x}$", "- <!--\n$\\operatorname{x}$", "> <!--\n```math\n\\operatorname{x}\n```"):
            self.assertTrue(any(e.code == "UNCERTIFIED_MACRO" for e in errors(text)))
        self.assertEqual(errors("<!--\n$\\operatorname{x}$"), [])

    def test_code_span_cannot_cross_table_cells_or_rows(self):
        for text in ("a | b\n--- | ---\n`foo | $\\operatorname{x}$ `", "a | b\n--- | ---\n`foo | b\nbar | $\\operatorname{x}$ `"):
            self.assertTrue(any(e.code == "UNCERTIFIED_MACRO" for e in errors(text)))

    def test_context_findings_retain_cli_json_locations(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested.md"
            path.write_text("> ```text\n> literal\n$\\operatorname{x}$\n", encoding="utf8")
            run = subprocess.run([sys.executable, str(MODULE), str(path), "--strict-portable", "--json"], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            findings = json.loads(run.stdout)["issues"]
            self.assertTrue(any(e["code"] == "UNCERTIFIED_MACRO" and e["line"] == 3 and e["path"] == str(path) for e in findings))

    def test_code_span_cannot_hide_other_blocks(self):
        for text in ("`foo\n# $\\operatorname{x}$ `", "`foo\n- $\\operatorname{x}$ `", "> `foo\n# $\\operatorname{x}$ `"):
            self.assertTrue(any(e.code == "UNCERTIFIED_MACRO" and e.line == 2 for e in errors(text)))
        self.assertEqual(errors("a | b\n--- | ---\n> $|x|$"), [])

    def test_comment_marker_inside_multiline_code(self):
        text = "`inline\n<!-- literal\nend`\n$\\newcommand{x}{y}$"
        self.assertTrue(any(e.code == "UNSAFE_MACRO" and e.line == 4 for e in errors(text)))

    def test_fence_containers_and_mutations(self):
        for prefix, close in (("", ""), ("> ", "> "), ("- ", "  ")):
            body = prefix + "```math\n" + close + r"\newcommand{a}{b}" + "\n" + close + "```"
            self.assertTrue(any(e.code == "UNSAFE_MACRO" and e.line == 2 for e in errors(body)))
            self.assertTrue(any(e.code == "BRACES" for e in errors(body.replace(r"\newcommand{a}{b}", "{x"))))
        self.assertTrue(any(e.code == "UNSAFE_MACRO" and e.line == 3 for e in errors("> ```text\n> harmless\n$\\newcommand{x}{y}$")))
        self.assertTrue(any(e.code == "UNSAFE_MACRO" for e in errors("```bad`info\n$\\newcommand{x}{y}$")))
        self.assertTrue(any(e.code == "UNSAFE_MACRO" for e in errors("~~~math\n\\newcommand{x}{y}\n~~~")))

    def test_svg_banner(self):
        import xml.etree.ElementTree as ET
        root = ET.parse(Path(__file__).resolve().parents[1] / "assets" / "smptex-test-pattern.svg").getroot()
        ns = {"svg":"http://www.w3.org/2000/svg"}
        bars = [r for r in root.findall("svg:rect", ns) if r.attrib.get("height") == "77"]
        self.assertEqual(len(bars), 7)
        strings = [node.text for node in root.findall("svg:text", ns)]
        self.assertIn("PLEASE STAND BY — MATHJAX FAILURE", strings)

    def test_valid_inline(self):
        self.assertEqual(errors("A $x^2+y^2=z^2$ works."), [])

    def test_valid_inline_backtick(self):
        self.assertEqual(errors("Safe with punctuation: $`a_b + x^{2}`$."), [])

    def test_valid_display(self):
        self.assertEqual(errors("Before\n\n$$\n\\frac{a}{b}=c\n$$\n\nAfter"), [])

    def test_valid_fenced_math(self):
        self.assertEqual(errors("```math\n\\begin{aligned}\na&=b\\\\\nc&=d\n\\end{aligned}\n```"), [])

    def test_literal_code_is_not_parsed(self):
        self.assertEqual(errors("Text `\\operatorname{Tr}` and `$broken`.\n\n```text\n$broken\n```"), [])

    def test_official_currency_span(self):
        self.assertEqual(errors("The price is <span>$</span>100 and $100/2=50$."), [])

    def test_escaped_currency(self):
        self.assertEqual(errors(r"Price \\$100? No, see $x=1$.".replace(r"\\$", r"\$")), [])

    def test_markdown_table_safe_math(self):
        self.assertEqual(errors("| Variable | Math |\n| --- | --- |\n| A | $a\\mid b$ |"), [])

    def test_markdown_table_raw_pipe_detected(self):
        self.assertTrue(any(e.code == "TABLE_PIPE" for e in errors("| name | formula |\n| --- | --- |\n| A | $|x|$ |")))

    def test_bad_inline(self):
        self.assertTrue(any(e.code == "UNTERMINATED_INLINE" for e in errors("An equation $a+b.")))

    def test_bad_display(self):
        self.assertTrue(any(e.code == "UNTERMINATED_DISPLAY" for e in errors("$$\nx+y")))

    def test_bad_braces(self):
        self.assertTrue(any(e.code == "BRACES" for e in errors(r"$\frac{1}{x$")))

    def test_bad_environment(self):
        self.assertTrue(any(e.code == "ENVIRONMENT" for e in errors("```math\n\\begin{aligned} a &= b\n```")))

    def test_bad_left_right(self):
        self.assertTrue(any(e.code == "LEFT_RIGHT" for e in errors(r"$\left( a+b$")))

    def test_bare_tex(self):
        self.assertTrue(any(e.code == "BARE_TEX" for e in errors(r"Oops: \frac{1}{2}")))

    def test_alt_delimiter(self):
        self.assertTrue(any(e.code == "ALT_DELIMITER" for e in errors(r"Oops: \(x+1\)")))

    def test_strict_operatorname(self):
        self.assertTrue(any(e.code == "UNCERTIFIED_MACRO" for e in errors(r"$\operatorname{rank}(A)$")))
        self.assertEqual(errors(r"$\operatorname{rank}(A)$", strict=False), [])

    def test_observed_operator_ab_contexts(self):
        # Regression coverage for the three observed GitHub Markdown contexts.
        contexts = (
            ("inline", r"$\mathrm{rank}(A)=2$", r"$\operatorname{rank}(A)=2$"),
            ("display", "$$\n\\mathrm{rank}(A)=2\n$$", "$$\n\\operatorname{rank}(A)=2\n$$"),
            ("math fence", "```math\n\\mathrm{rank}(A)=2\n```", "```math\n\\operatorname{rank}(A)=2\n```"),
        )
        for name, control, challenge in contexts:
            with self.subTest(context=name):
                self.assertEqual(errors(control), [])
                self.assertEqual(errors(challenge, strict=False), [])
                self.assertTrue(any(e.code == "UNCERTIFIED_MACRO" for e in errors(challenge)))

    def test_portable_operator(self):
        self.assertEqual(errors(r"$\mathrm{rank}(A)$"), [])

    def test_nopreamble(self):
        self.assertTrue(any(e.code == "UNSAFE_MACRO" for e in errors(r"$\newcommand{\foo}{x}$")))

    def test_isolated_display_policy(self):
        self.assertTrue(any(e.code == "DISPLAY_DELIMITER" for e in errors("Text $$x$$")))

    def test_fence_missing(self):
        self.assertTrue(any(e.code == "UNTERMINATED_FENCE" for e in errors("```math\nx=y")))
        codes = {e.code for e in errors("```math\n" + r"\newcommand{a}{x")}
        self.assertTrue({"UNTERMINATED_FENCE", "UNSAFE_MACRO", "BRACES"} <= codes)

    def test_unclosed_noncoding_fence(self):
        self.assertTrue(any(e.code == "UNTERMINATED_FENCE" for e in errors("```python\nprint('x')")))

    def test_control_broken_mutation(self):
        good = "$$\n\\sum_{n=1}^{N} n = N(N+1)/2\n$$"
        bad = good.replace("_{n=1}", "_{n=1")
        self.assertEqual(errors(good), [])
        self.assertTrue(errors(bad))


if __name__ == "__main__":
    unittest.main()
