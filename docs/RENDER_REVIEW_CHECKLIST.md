# SMPTeX · Human render review

[← Back to SMPTeX](../README.md) · [Test card](GITHUB_MATH_TEST_CARD.md) · [Operator probe](probes/OPERATORNAME_AB.md) · [Ledger](MATH_COMPATIBILITY_LEDGER.md)

Open the pages in a browser on **GitHub's rendered file view**, not Raw or a locally generated preview. Check each line **only if visually observed**. The 22 checked items below record the historical user report; its viewed commit and browser versions are unknown, so it is not a current universal certification. Operator checks have separate screenshot evidence. For a new review, use the [ledger](MATH_COMPATIBILITY_LEDGER.md) and record the exact revision, surface and client.

**Reference file:** [Test card](GITHUB_MATH_TEST_CARD.md); exact viewed commit **UNVERIFIED**  
**Review date:** 2026-10-23 EDT (exact time unknown)  
**Surface:** GitHub repository Markdown  
**Viewing contexts:** phone web browser and PC web browser (names/versions unknown)

## Test card · T00–T21

- [x] T00 · Inline equation — **PASS · USER-REPORTED** (phone + PC)
- [x] T01 · GitHub protected inline equation — **PASS · USER-REPORTED** (phone + PC)
- [x] T02 · Display-dollar equation — **PASS · USER-REPORTED** (phone + PC)
- [x] T03 · Fenced `math` block — **PASS · USER-REPORTED** (phone + PC)
- [x] T04 · Greek letters, indices and adornments — **PASS · USER-REPORTED** (phone + PC)
- [x] T05 · Blackboard, calligraphic and upright type — **PASS · USER-REPORTED** (phone + PC)
- [x] T06 · Aligned multiline math — **PASS · USER-REPORTED** (phone + PC)
- [x] T07 · Matrix and determinant — **PASS · USER-REPORTED** (phone + PC)
- [x] T08 · Piecewise function — **PASS · USER-REPORTED** (phone + PC)
- [x] T09 · Calculus operators — **PASS · USER-REPORTED** (phone + PC)
- [x] T10 · Categorical composition and arrows — **PASS · USER-REPORTED** (phone + PC)
- [x] T11 · Bra-ket and tensor notation — **PASS · USER-REPORTED** (phone + PC)
- [x] T12 · Euler product — **PASS · USER-REPORTED** (phone + PC)
- [x] T13 · Ring quotients — **PASS · USER-REPORTED** (phone + PC)
- [x] T14 · Quantifiers and set braces — **PASS · USER-REPORTED** (phone + PC)
- [x] T15 · Paired delimiters — **PASS · USER-REPORTED** (phone + PC)
- [x] T16 · `\mathrm` and `\text` — **PASS · USER-REPORTED** (phone + PC)
- [x] T17 · TLICA diagnostic vector — **PASS · USER-REPORTED** (phone + PC)
- [x] T18 · SUCC/FUCC kets — **PASS · USER-REPORTED** (phone + PC)
- [x] T19 · Currency dollar versus math delimiter — **PASS · USER-REPORTED** (phone + PC)
- [x] T20 · High-density aligned equation — **PASS · USER-REPORTED** (phone + PC)
- [x] T21 · Math inside Markdown table — **PASS · USER-REPORTED** (phone + PC)

## Operator macro probe · P00–P05

**User screenshot observed 2026-10-23 EDT on mobile repository Markdown.** Checked below means *inspected*, not passed. The screenshot lacks an immutable commit URL or client identifier; [ledger](MATH_COMPATIBILITY_LEDGER.md).

- [x] P00 · Inline `\mathrm` control — **PASS** (user screenshot)
- [x] P01 · Inline `\operatorname` challenge — **FAIL · macro not allowed** (user screenshot)
- [x] P02 · Display `\mathrm` control — **PASS** (user screenshot)
- [x] P03 · Display `\operatorname` challenge — **FAIL · macro not allowed** (user screenshot)
- [x] P04 · Math-fence `\mathrm` control — **PASS** (user screenshot)
- [x] P05 · Math-fence `\operatorname` challenge — **FAIL · macro not allowed** (user screenshot)

## Calibration verdict

The historical report recorded T00–T21 as 22/22 passing on phone and PC browsers, with no card failures reported. The separate mobile screenshot showed P00/P02/P04 passing and P01/P03/P05 explicitly rejected. Its exact client and viewed revision are not established.

A later desktop repository Preview observation at `84cbf0a` found a comma where T09 intended thin spacing and missing T14 set braces. The card was changed to math fences without changing those formulas; at pinned revision `1918795`, the reviewed T09 and T14 rendered the intended spacing and braces. At that later observation, T01, T05, T13 and T16 retained MathML variant attributes but visual differentiation of some blackboard and calligraphic glyphs was **AMBIGUOUS** at the available scale. These observations do not erase or independently verify the earlier report. Details, URLs, scope and further context observations are in the [ledger](MATH_COMPATIBILITY_LEDGER.md).

**Semantic check:** not established by appearance alone  
**Follow-up discriminator:** recheck ambiguous glyphs at suitable magnification and inspect the specific client and surface of interest.

For changed repository Markdown, optionally run `python scripts/math_guard.py path/to/changed.md --profile repository-preview --json`, replacing the example path. These conservative, nonzero-exit review prompts are based on selected desktop repository Preview observations; they are not render or mathematical certification. Intentional render probes are expected to produce profile findings and must also be source-checked with the default profile. The selected profile is included in JSON.

If a strip fails, file a [render regression](https://github.com/femboy2112/SMPTeX/issues/new?template=render-regression.md) and update the [ledger](MATH_COMPATIBILITY_LEDGER.md) with the precise evidence. A rendered symbol can still express incorrect mathematics; do not treat a pretty formula as a theorem certificate.
