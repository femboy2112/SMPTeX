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
        self.assertTrue(any(e.code == "TABLE_PIPE" for e in errors("| A | $|x|$ |")))

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

    def test_unclosed_noncoding_fence(self):
        self.assertTrue(any(e.code == "UNTERMINATED_FENCE" for e in errors("```python\nprint('x')")))

    def test_control_broken_mutation(self):
        good = "$$\n\\sum_{n=1}^{N} n = N(N+1)/2\n$$"
        bad = good.replace("_{n=1}", "_{n=1")
        self.assertEqual(errors(good), [])
        self.assertTrue(errors(bad))


if __name__ == "__main__":
    unittest.main()
