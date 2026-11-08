"""Source-only consumer reductions. GitHub rendering needs a separate live probe."""
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "math_guard.py"
spec = importlib.util.spec_from_file_location("smptex_consumer_guard", MODULE)
guard = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = guard
spec.loader.exec_module(guard)

# SUCC #545, docs/PI_NORMALITY_FRONTIER.md:72-74 at d32342d375f44ddf62221ad6aff2f534abdc0a03.
# The inequality and interval arguments are preserved byte-for-byte; normality is OPEN.
SUCC_LS = r"Λ_A=\sup_{1\le a<b\le8,\ b-a\ge1/4}\ \sup_t\ \bigl|μ_{[aA,bA)}([0,t))-μ_{[A,2A)}([0,t))\bigr|\ \longrightarrow\ 0 ."
# FuckingRH #24, wiki/02-the-rh-equivalent-target.md:16,11 at
# 11764fcad3551e4dcce95d06d0370a2cd31470e1. This wiki/ directory is a repo file.
RH_XI = r"\xi(s) = \tfrac12\, s(s-1)\, \pi^{-s/2}\, \Gamma(s/2)\, \zeta(s)."
RH_RE = r"\mathrm{Re}\, s > 1"
# SUCC Wiki The-Riemann-Connection, last-modified commit 90e7f4e266915c7de3097c44b4594470524feb06
# in local wiki checkout ae31f66ad6afd42225f164f5cbce89f6979f6851.
# The immutable Wiki revision was inspected in desktop Chrome on 2026-11-08 UTC.
# This source test alone does not establish rendering on another surface.
WIKI_MATRIX = r"\begin{pmatrix} 2 & -14\cr -14 & 2 \end{pmatrix}"


def codes(source):
    return [issue.code for issue in guard.Scanner("consumer.md", strict_portable=True).scan(source)]


def fence(tex):
    return "```math\n" + tex + "\n```\n"


class ConsumerReductionTests(unittest.TestCase):
    def test_succ_legacy_delimiter_is_detected(self):
        legacy = "\\[\n" + SUCC_LS + "\n\\]"
        self.assertIn("ALT_DELIMITER", codes(legacy))
        # Same source in a fenced context must at least be checked for valid grouping.
        self.assertEqual(codes(fence(SUCC_LS)), [])
        self.assertIn("BRACES", codes(fence(SUCC_LS.replace("1/4}", "1/4", 1))))

    def test_completed_zeta_and_real_part_are_source_checked(self):
        # Actual broken rendering includes commas in these contexts, despite recognition;
        # these source assertions do not certify a renderer or the candidate alternatives.
        self.assertIn("DISPLAY_DELIMITER", codes("$$" + RH_XI + "$$"))
        self.assertEqual(codes(fence(RH_XI)), [])
        self.assertEqual(codes("$`" + RH_RE + "`$"), [])
        self.assertIn("BRACES", codes(fence(RH_XI.replace("{-s/2}", "{-s/2", 1))))

    def test_two_row_wiki_matrix_preserves_grouping(self):
        self.assertEqual(codes(fence(WIKI_MATRIX)), [])
        self.assertIn("ENVIRONMENT", codes(fence(WIKI_MATRIX.replace(r"\end{pmatrix}", "", 1))))


if __name__ == "__main__":
    unittest.main()
