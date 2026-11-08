# Section to place in AGENTS.md and/or CLAUDE.md: GitHub math contract

> Copy this section into your actual repository agent instructions (or reference the file from those instructions) so it is visible to Codex and Claude before edits.

## Markdown mathematics: SMPTeX contract

**Target output:** equations must be correct *and* render on the actual target GitHub surface. Read `docs/GITHUB_MATH_TEST_CARD.md` and `docs/MATH_COMPATIBILITY_LEDGER.md` before math-heavy documentation edits.

1. Use documented GitHub math syntax: `$...$` for simple inline math, `$`backtick delimiters for inline material that collides with Markdown parsing, and separate-line `$$...$$` or fenced `math` for displays. Do not use `\(...\)` or `\[...\]` as the default GitHub source convention.
2. Prefer portable primitives: `\frac`, `\sqrt`, `\sum`, `\prod`, `\mathbb`, `\mathcal`, `\mathrm`, `\text`, `\begin{aligned}`, `\begin{pmatrix}`, and `\begin{cases}`. A command being supported by LaTeX **does not** imply it is supported in GitHub's MathJax configuration.
3. For the rank/trace/closure family, prefer `\mathrm{rank}`, `\mathrm{Tr}`, `\mathrm{Cl}`. **A same-page GitHub mobile repository-Markdown A/B observation on 2026-10-23 found `\operatorname` explicitly rejected in inline, display, and math-fence contexts.** Do not blindly rewrite spacing-sensitive named operators: `\mathrm` produces upright letters but not all operator spacing and limits semantics. This does not establish a universal MathJax ban. See the ledger.
4. Do not silently introduce package imports, document preambles, global macros, TikZ, or LaTeX-only diagram environments into Markdown equations. Use separate diagrams where necessary, with explicit provenance and preview checks.
5. Run the checks below for math-bearing Markdown edits. The strict exclusion names only the intentional operator A/B negative fixture; its separate non-strict scan still checks its math syntax. If a consumer does not install this fixture, omit both the exclusion and the separate probe command. Fix source failures unless the guard has a demonstrated false positive.

   ```bash
   python -m unittest discover -s tests -v
   python scripts/math_guard.py . --strict-portable --exclude docs/probes/OPERATORNAME_AB.md
   python scripts/math_guard.py docs/probes/OPERATORNAME_AB.md
   python scripts/mobile_fallback.py
   ```

   The final command checks the committed fallback artifacts if the consumer installs them; it is not a GitHub render test.

   For a changed repository Markdown file, additionally consider
   `python scripts/math_guard.py path/to/changed.md --profile repository-preview --json`.
   Replace the example path. This opt-in profile reports conservative risks from
   observed desktop repository Preview cases and returns nonzero for findings;
   `source` remains the default and JSON names the selected profile. Review the
   actual target and intended symbols; a finding is not proof that the source
   fails there. Intentional render probes are expected to produce profile
   findings and must still receive separate default source checks. The profile
   does not certify Wiki, other clients, the native Android app, or mathematics.
6. Source guard success is **not** a render certificate. For modified math components not covered by a previously observed matching calibration, open the rendered GitHub page after committing on a non-main branch; record its exact URL, commit, and observed status in the ledger. Never claim a visual check if no browser/UI inspection occurred.
7. After visual certification, separately review **semantic fidelity**: delimiters, quantifier scope, symbols, map direction, domain/codomain, indices, signs, and assumptions. Do not 'fix' a rendering failure by changing the asserted theorem.
8. When recording a failure, produce a minimal reproducer, a working nearby control, a failing challenge, and a cross-surface note (repo/wiki/PR). Prefer discriminating probes over global bans inferred from one broken example.

**Definition of done:** source linter green; math unit/mutation controls green; target renderer observed or marked UNVERIFIED; mathematical statement independently checked to the level its claim requires; ledger updated for novel macros/contexts.