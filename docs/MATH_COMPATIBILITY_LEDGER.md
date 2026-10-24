# SMPTeX · GitHub Rendering Compatibility Ledger

[← README](../README.md) · [Live test card](GITHUB_MATH_TEST_CARD.md) · [A/B probe](probes/OPERATORNAME_AB.md) · [Review checklist](RENDER_REVIEW_CHECKLIST.md)

## Calibrated layers

| Claim | Status | Evidence | Limit |
| --- | --- | --- | --- |
| GitHub documents `$...$`, `$`backtick delimiters, `$$...$$`, and fenced `math` | DOCUMENTED | [GitHub Math Docs](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions) | Documentation is not a specific live test |
| GitHub Markdown math uses MathJax | DOCUMENTED | GitHub Math Docs | Package/configuration details may vary |
| Upstream MathJax documents `\operatorname` | DOCUMENTED UPSTREAM | [MathJax macro list](https://docs.mathjax.org/en/stable/input/tex/macros/) | Not live GitHub visual evidence |
| SMPTeX guard catches specified syntax failures | SOURCE-CHECKED LOCALLY | `tests/test_math_guard.py`; reproducible commands in README | Not a complete parser |
| T00–T21 rendered on SMPTeX GitHub Markdown | **UNVERIFIED** | [Current test card](GITHUB_MATH_TEST_CARD.md) | Awaiting independent human visual inspection |
| P00–P05 live operator probe rendered on GitHub | **UNVERIFIED** | [Current probe](probes/OPERATORNAME_AB.md) | A failure without passing control is ambiguous |
| Mathematical semantics of outside research correct | NOT TESTED BY SMPTeX | Requires independent mathematical analysis | Correct appearance does not prove correctness |

## Evidence records

| Date UTC | ID(s) | GitHub surface | Exact file URL + SHA | Source preflight | Actual browser observation | Verdict | Screenshot / repro |
| --- | --- | --- | --- | --- | --- | --- | --- |
| — | T00–T21 | Repo Markdown | [Test card](GITHUB_MATH_TEST_CARD.md); SHA pending | Locally testable | Not yet inspected | UNVERIFIED | [Review checklist](RENDER_REVIEW_CHECKLIST.md) |
| — | P00–P05 | Repo Markdown | [Live probe](probes/OPERATORNAME_AB.md); SHA pending | Non-strict source check required | Not yet inspected | UNVERIFIED | Operator A/B control |

## How to change a verdict

1. Open the exact **GitHub-rendered** page at an immutable commit. Log SHA, URL, UTC date, and browser.
2. Compare actual rendered output to expected output for each strip. Note whether a *control* passed before interpreting a challenge failure.
3. Preserve screenshots or a reproducible description. Prefer a minimal passing control and a minimal failing case in the **same** Markdown context.
4. Distinguish SOURCE-CHECKED, VISUALLY OBSERVED, SEMANTICALLY REVIEWED. Use **UNVERIFIED** for a stage that did not run and **AMBIGUOUS** for an observed failure whose mechanism cannot be identified.
5. For wiki/PR/issue rendering, run a new check **on that surface** rather than transferring a repo-page result as proof.

**Important:** a GitHub Markdown API result is not necessarily a complete MathJax browser render. Wiki files live in a separate Git repository and require their own audit.
