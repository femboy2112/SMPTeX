# Codex / Claude Installation Prompt · SMPTeX

You are performing **an implementation round**, not writing another roadmap. Install the supplied **SMPTeX GitHub math calibration kit** into the current repository, preserving project history, research correctness, and existing agent instructions.

## First: recover reality

- Inspect the actual repository, working tree, branch, default branch, remote, commit SHA, existing `AGENTS.md` and `CLAUDE.md`, GitHub Actions conventions, and the math-heavy documentation surfaces.
- Read `README.md`, `docs/GITHUB_MATH_TEST_CARD.md`, `docs/MATH_COMPATIBILITY_LEDGER.md`, `scripts/math_guard.py`, `tests/test_math_guard.py`, and `AGENTS_MATH_PROTOCOL.md` from the kit.
- Read GitHub's official math-formatting guide, then distinguish **documented syntax**, **linter-observed syntax**, **upstream MathJax macro availability**, and **visually observed rendering on the actual GitHub surface**. Do not collapse these categories.
- Work from a fresh, non-main branch. Do not overwrite local changes, existing instructions, CI conventions, or wiki content.

## Deliverable 1: a functioning calibration surface

- Integrate the test card and compatibility ledger under the repository's documentation tree.
- Merge the SMPTeX agent contract with existing instructions without deleting or contradicting existing policies. Do not claim agents automatically read `AGENTS_MATH_PROTOCOL.md` unless it is actually referenced or incorporated in instructions they ingest.
- Integrate the source guard and its full test set. Check for false positives against the project's current Markdown corpus before enabling a blanket CI failure gate. If legacy debt is large, stage the rollout (modified files first, then repository-wide) and write down the residual debt; do not edit research claims to satisfy a parser.
- Add a **path-filtered** workflow consistent with project CI policy. It must not start costly builds for unrelated non-doc changes. Preserve existing workflow names and YAML formatting.

## Deliverable 2: controls and validation

Run at least:

```bash
python -m unittest discover -s tests -v
python scripts/math_guard.py . --strict-portable
```

Preserve the actual outputs and exit codes. Add project-specific positive/negative/mutation fixtures where failures were encountered. For each novel macro, distinguish source parse failures, Markdown boundary collisions, MathJax syntax failures, and mathematical semantic mistakes.

Specifically A/B probe `\mathrm{rank}` versus `\operatorname{rank}` in the **same live GitHub context** before declaring the latter universally broken. The upstream MathJax command list is not a certification of GitHub's particular configuration. GitHub's Markdown REST render endpoint tests a different part of the pipeline from final browser rendering.

Where browser access is available, publish the card to the temporary branch, open the **rendered GitHub page**, inspect every T00–T21 strip, and fill in the compatibility ledger with the exact URL, SHA, date, surface, expected/actual result, and any screenshot or trace. If browsing is unavailable, mark the visual stage **UNVERIFIED**, not PASS.

## Deliverable 3: useful migration, not indiscriminate churn

- Inventory common math breakages in project docs, wiki, research fronts, theorem statements, and README files.
- Fix high-frequency mechanically verifiable formatting issues, preserving mathematical meanings and stable links.
- When rewriting a formula, compare the original and rewritten mathematical expressions for semantic equivalence. Changes of hypothesis, signs, quantifier scope, domain, codomain, operators, or claims require independent mathematical review.
- Do not rewrite huge documents just because they contain a few questionable macros. Fix a minimal representative sample, add regression tests, then systematically proceed.
- GitHub wiki is a separate repository: assess its state, repository/permission access, and instructions independently. Do not assume main-repo CI covers it.

## Completion and reporting

Commit coherent units to the research branch; push only intended changes; open a PR when appropriate. Do **not** merge to main without the requested review or authorization. Report:

1. Exact initial and final branch/head SHA, plus added/modified files.
2. Test outputs, pass/fail outcomes, observed vs unverified rendering, and the compatibility ledger delta.
3. Actual high-priority documentation repairs, remaining risks and false positives.
4. A final GitHub link to the calibration test card and PR (only if created).
5. The next smallest verdict-changing probe if visual rendering or macro status remains unresolved.

**Success criterion:** future agents can copy known-working patterns, fail fast on common mistakes, and can no longer equate “my Markdown looked plausible” with “GitHub actually rendered the intended mathematics.”
