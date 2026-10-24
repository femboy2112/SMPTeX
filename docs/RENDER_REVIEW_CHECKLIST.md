# SMPTeX · Human render review

[← Back to SMPTeX](../README.md) · [Test card](GITHUB_MATH_TEST_CARD.md) · [Operator probe](probes/OPERATORNAME_AB.md) · [Ledger](MATH_COMPATIBILITY_LEDGER.md)

Open the two pages in a browser on **GitHub's rendered file view**, not Raw or a locally generated preview. Check each line **only if visually observed**. The checklist is intentionally not pre-checked.

**Reference URL:** _paste exact rendered GitHub link_  
**Commit:** _full SHA_  
**Review date/time:** _UTC_  
**Surface:** _repository Markdown / pull request / wiki_  
**Browser/context:** _browser and version, if relevant_

## Test card · T00–T21

- [ ] T00 · Inline equation
- [ ] T01 · GitHub protected inline equation
- [ ] T02 · Display-dollar equation
- [ ] T03 · Fenced `math` block
- [ ] T04 · Greek letters, indices and adornments
- [ ] T05 · Blackboard, calligraphic and upright type
- [ ] T06 · Aligned multiline math
- [ ] T07 · Matrix and determinant
- [ ] T08 · Piecewise function
- [ ] T09 · Calculus operators
- [ ] T10 · Categorical composition and arrows
- [ ] T11 · Bra-ket and tensor notation
- [ ] T12 · Euler product
- [ ] T13 · Ring quotients
- [ ] T14 · Quantifiers and set braces
- [ ] T15 · Paired delimiters
- [ ] T16 · `\mathrm` and `\text`
- [ ] T17 · TLICA diagnostic vector
- [ ] T18 · SUCC/FUCC kets
- [ ] T19 · Currency dollar versus math delimiter
- [ ] T20 · High-density aligned equation
- [ ] T21 · Math inside Markdown table

## Operator macro probe · P00–P05

**User screenshot observed 2026-10-23 EDT on mobile repository Markdown.** Checked below means *inspected*, not passed. The screenshot lacks an immutable commit URL or client identifier; [ledger](MATH_COMPATIBILITY_LEDGER.md).

- [x] P00 · Inline `\mathrm` control — **PASS** (user screenshot)
- [x] P01 · Inline `\operatorname` challenge — **FAIL · macro not allowed** (user screenshot)
- [x] P02 · Display `\mathrm` control — **PASS** (user screenshot)
- [x] P03 · Display `\operatorname` challenge — **FAIL · macro not allowed** (user screenshot)
- [x] P04 · Math-fence `\mathrm` control — **PASS** (user screenshot)
- [x] P05 · Math-fence `\operatorname` challenge — **FAIL · macro not allowed** (user screenshot)

## Calibration verdict

**Status:** UNVERIFIED / PASS / FAIL / AMBIGUOUS  
**Failed strip IDs:** _list_  
**Observed symptoms:** _copy text, screenshot path, or issue link_  
**Semantic check:** _performed separately? by whom and at which level?_  
**Follow-up discriminator:** _what control would change the verdict?_

If a strip fails, file a [render regression](https://github.com/femboy2112/SMPTeX/issues/new?template=render-regression.md) and update the [ledger](MATH_COMPATIBILITY_LEDGER.md) with the precise evidence. A rendered symbol can still express incorrect mathematics; do not treat a pretty formula as a theorem certificate.
