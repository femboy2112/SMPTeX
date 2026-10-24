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
| P00–P05 A/B on mobile repository Markdown | **VISUALLY OBSERVED**: P00/P02/P04 PASS, P01/P03/P05 FAIL | Screenshot supplied Oct 23 2026 EDT; [probe](probes/OPERATORNAME_AB.md) | Client and viewed SHA not visible; wiki/PR/desktop unverified |
| Mathematical semantics of outside research correct | NOT TESTED BY SMPTeX | Requires independent mathematical analysis | Correct appearance does not prove correctness |

## Evidence records

| Date UTC | ID(s) | GitHub surface | Exact file URL + SHA | Source preflight | Actual browser observation | Verdict | Screenshot / repro |
| --- | --- | --- | --- | --- | --- | --- | --- |
| — | T00–T21 | Repo Markdown | [Test card](GITHUB_MATH_TEST_CARD.md); SHA pending | Locally testable | Not yet inspected | UNVERIFIED | [Review checklist](RENDER_REVIEW_CHECKLIST.md) |
| 2026-10-24 UTC (Oct 23 EDT) | P00/P02/P04 | Mobile repository Markdown | [Reference fixture at main@da7c846](https://github.com/femboy2112/SMPTeX/blob/da7c8463fce31548414ba476c843722daf81bb7e/docs/probes/OPERATORNAME_AB.md); viewed SHA not shown | Non-strict source check | Upright `rank(A)=2` rendered in all three contexts | **PASS · OBSERVED** | User screenshot provided in conversation; exact client unverified |
| 2026-10-24 UTC (Oct 23 EDT) | P01/P03/P05 | Mobile repository Markdown | [Reference fixture at main@da7c846](https://github.com/femboy2112/SMPTeX/blob/da7c8463fce31548414ba476c843722daf81bb7e/docs/probes/OPERATORNAME_AB.md); viewed SHA not shown | Non-strict source check | `The following macros are not allowed: operatorname` appears in all three contexts | **FAIL · OBSERVED** | Same-page positive controls pass |

## Observed counterexample · O-2026-10-23-MOBILE-OPERATORNAME

- **Raw observation:** screenshot supplied in conversation shows all six probes in one mobile GitHub-rendered Markdown view: three `\mathrm` controls correctly display upright mathematics, while the three `\operatorname` challenges fail with an explicit forbidden-macro error.
- **Discrimination:** each same-context A/B pair changes the macro while leaving the expression structure fixed; passing controls reject the rival explanation that GitHub math is globally broken on that view.
- **Provenance boundary:** screenshot does not contain full URL, viewed commit, or exact client. Its text matches the reference fixture at `main@da7c846`, but screenshot-to-commit binding remains **UNVERIFIED**. Date is the user-submission date (not embedded on the screen).
- **Independent historical precedent:** [github/markup #1688](https://github.com/github/markup/issues/1688) reports the same message from 2023. It does not establish behavior for all current GitHub surfaces.
- **Portable policy:** avoid `\operatorname` in ordinary GitHub-targeted Markdown; use tested `\mathrm` for simple upright words. Operator spacing and limits are different; review any rewrite for mathematical meaning.
- **Outstanding:** test wiki, Issue/PR comments, desktop clients, other macros, and the T00–T21 test card. Record client and immutable URL in a follow-up run.
- **Evidence storage:** original screenshot remains in the user conversation and is not publicly hosted in this repo; a redacted screenshot attachment would strengthen independent reproducibility.

## How to change a verdict

1. Open the exact **GitHub-rendered** page at an immutable commit. Log SHA, URL, UTC date, and browser.
2. Compare actual rendered output to expected output for each strip. Note whether a *control* passed before interpreting a challenge failure.
3. Preserve screenshots or a reproducible description. Prefer a minimal passing control and a minimal failing case in the **same** Markdown context.
4. Distinguish SOURCE-CHECKED, VISUALLY OBSERVED, SEMANTICALLY REVIEWED. Use **UNVERIFIED** for a stage that did not run and **AMBIGUOUS** for an observed failure whose mechanism cannot be identified.
5. For wiki/PR/issue rendering, run a new check **on that surface** rather than transferring a repo-page result as proof.

**Important:** a GitHub Markdown API result is not necessarily a complete MathJax browser render. Wiki files live in a separate Git repository and require their own audit.
