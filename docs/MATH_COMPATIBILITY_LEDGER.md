# SMPTeX · GitHub Rendering Compatibility Ledger

[← README](../README.md) · [Live test card](GITHUB_MATH_TEST_CARD.md) · [A/B probe](probes/OPERATORNAME_AB.md) · [Review checklist](RENDER_REVIEW_CHECKLIST.md)

## Calibrated layers

| Claim | Status | Evidence | Limit |
| --- | --- | --- | --- |
| GitHub documents `$...$`, `$`backtick delimiters, `$$...$$`, and fenced `math` | DOCUMENTED | [GitHub Math Docs](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions) | Documentation is not a specific live test |
| GitHub Markdown math uses MathJax | DOCUMENTED | GitHub Math Docs | Package/configuration details may vary |
| Upstream MathJax documents `\operatorname` | DOCUMENTED UPSTREAM | [MathJax macro list](https://docs.mathjax.org/en/stable/input/tex/macros/) | Not live GitHub visual evidence |
| SMPTeX guard catches specified syntax failures | SOURCE-CHECKED LOCALLY | `tests/test_math_guard.py`; reproducible commands in README | Not a complete parser |
| T00–T21 on GitHub repository Markdown | **PASS — USER-REPORTED VISUAL OBSERVATION (22/22 phone; 22/22 PC)** | User report dated 2026-10-23 EDT; [test card](GITHUB_MATH_TEST_CARD.md) | Exact viewed SHA, browser versions and screenshots not provided; not independently re-observed by assistant |
| GitHub Android-app view of T00–T21 card | **PRESENTATION CONCERN — USER REPORT + SCREENSHOT** | User-supplied long Android app screenshot, 2026-10-23 EDT | Capture is only 72 px wide after attachment processing; no per-strip render failures or root cause demonstrated; app version/commit unknown |
| P00–P05 A/B on mobile repository Markdown | **VISUALLY OBSERVED**: P00/P02/P04 PASS, P01/P03/P05 FAIL | Screenshot supplied Oct 23 2026 EDT; [probe](probes/OPERATORNAME_AB.md) | Client and viewed SHA not visible; wiki/PR/desktop unverified |
| Static PNG image fallback on GitHub Android | **UNVERIFIED ON DEVICE — GENERATED REFERENCE** | [Mobile fallback](MOBILE_APP_FALLBACK.md); built from T00–T21 with source and PNG digests | Math in PNG images can display even when the Markdown TeX parser is absent; PNG display is never a native math-render pass |
| Mathematical semantics of outside research correct | NOT TESTED BY SMPTeX | Requires independent mathematical analysis | Correct appearance does not prove correctness |

## Evidence records

| Date / timezone | ID(s) | GitHub surface | Reference file / provenance | Source preflight | Actual browser observation | Verdict | Screenshot / repro |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-23 EDT; time not supplied | T00–T21 | GitHub repo Markdown — phone browser | [Reference source at main@3f1d20d](https://github.com/femboy2112/SMPTeX/blob/3f1d20d5624f0fe32ff60e1016f0039f2aef430f/docs/GITHUB_MATH_TEST_CARD.md); viewed SHA unverified | Existing source preflight | User reports all 22 rendered perfectly | **22/22 PASS · USER-REPORTED** | ChatGPT report; no card screenshot/browser version |
| 2026-10-23 EDT; time not supplied | T00–T21 | GitHub repo Markdown — PC browser | [Reference source at main@3f1d20d](https://github.com/femboy2112/SMPTeX/blob/3f1d20d5624f0fe32ff60e1016f0039f2aef430f/docs/GITHUB_MATH_TEST_CARD.md); viewed SHA unverified | Existing source preflight | User reports all 22 rendered perfectly | **22/22 PASS · USER-REPORTED** | ChatGPT report; no card screenshot/browser version |
| 2026-10-23 EDT; time not supplied | T00–T21 page | GitHub Android app (not phone browser) | [Reference source at main@0ac5091](https://github.com/femboy2112/SMPTeX/blob/0ac509184bba5f95cdfab749f8536712ac285ccd/docs/GITHUB_MATH_TEST_CARD.md); viewed SHA unverified | Same repository math source; no app-targeted static check | User reports bad app presentation; supplied long screenshot is cramped / difficult to inspect | **APP UX CONCERN · USER-REPORTED; STRIP FAILURES UNVERIFIED** | User screenshot in conversation; app version unknown; capture/attachment downscaling may affect readability |
| 2026-10-24 UTC (Oct 23 EDT) | P00/P02/P04 | Mobile repository Markdown | [Reference fixture at main@da7c846](https://github.com/femboy2112/SMPTeX/blob/da7c8463fce31548414ba476c843722daf81bb7e/docs/probes/OPERATORNAME_AB.md); viewed SHA not shown | Non-strict source check | Upright `rank(A)=2` rendered in all three contexts | **PASS · OBSERVED** | User screenshot provided in conversation; exact client unverified |
| 2026-10-24 UTC (Oct 23 EDT) | P01/P03/P05 | Mobile repository Markdown | [Reference fixture at main@da7c846](https://github.com/femboy2112/SMPTeX/blob/da7c8463fce31548414ba476c843722daf81bb7e/docs/probes/OPERATORNAME_AB.md); viewed SHA not shown | Non-strict source check | `The following macros are not allowed: operatorname` appears in all three contexts | **FAIL · OBSERVED** | Same-page positive controls pass |

## Repository Preview regression · 2026-11-08 UTC

At approximately 05:15 UTC, desktop cloud Chrome (exact version unavailable) viewed [the card at 84cbf0a7fd1ca1c0f949ccf8b7ab1208808af45e](https://github.com/femboy2112/SMPTeX/blob/84cbf0a7fd1ca1c0f949ccf8b7ab1208808af45e/docs/GITHUB_MATH_TEST_CARD.md) in GitHub repository file Preview. After typesetting, T09 contained a visible comma between x squared and dx where the source calls for thin spacing, and T14 omitted the expected visible set braces. The accessibility tree also contained the comma and lacked the set braces. On the same page, protected-inline T01 retained its braces and fenced-math T03 rendered. These are nearby controls, not a matched experiment establishing cause. This observation does not invalidate the earlier historical user reports, whose viewed revision and clients were not identified.

The card changes T09 and T14 from isolated-dollar display to math fences without changing their TeX source. The unchanged source digests match the existing static PNG references; checksum success is not a render test. The [matched context probe](probes/PUNCTUATION_CONTEXT.md) supplies the same spacing and brace expressions across four contexts and row/relation controls. For pinned repository Preview observations of the revised card and probe, see the next section; other surfaces and clients remain **UNVERIFIED**. The original failures remain reproducible at the pinned URL above; do not represent a future change in GitHub behavior as a source change.

## Pinned desktop repository Preview · 2026-11-08 UTC

At approximately 05:24 UTC, desktop cloud Chrome (version unavailable) inspected [card at 1918795de676db953cc1d4e720a984ceeef2c51a](https://github.com/femboy2112/SMPTeX/blob/1918795de676db953cc1d4e720a984ceeef2c51a/docs/GITHUB_MATH_TEST_CARD.md) and its [matched probe at the same SHA](https://github.com/femboy2112/SMPTeX/blob/1918795de676db953cc1d4e720a984ceeef2c51a/docs/probes/PUNCTUATION_CONTEXT.md). GitHub repository file Preview was the surface, not a Wiki, issue, PR-rendering, mobile browser or native-app test. The MathML was read only after typesetting; screenshots and the accessibility tree were also inspected. The observations below do not certify mathematical theorems or another client.

| Card strips | Observed result at this SHA |
| --- | --- |
| T00, T02–T04, T06–T12, T14–T15, T17–T21 | Source symbols and stated layout supported by rendered MathML and visual inspection, subject to the following qualification: T00, T06, T12 and T18 were checked in MathML; their complete visuals at this revision were not separately captured. T06's MathML has two rows and aligned columns. T07 has two rows and two columns; T08 has two cases; T20 has three rows. T09 has a thin-space MathML element and no comma before dx. T14 has both literal braces. |
| T01, T05, T13, T16 | Braces, relations, and other structure are present in MathML. The screenshot does not establish that blackboard-bold and calligraphic glyph variants are visually distinguishable: they appear like ordinary letters at available scale, although MathML retains the variant attributes. **AMBIGUOUS** until inspected at suitable magnification or on another identified client. |

| Matched probe | Plain inline | Protected inline | Isolated dollar display | Math fence |
| --- | --- | --- | --- | --- |
| A spacing | FAIL: comma | PASS: thin space, no comma | FAIL: comma | PASS: thin space, no comma |
| B literal braces | FAIL: braces absent | PASS: both braces | FAIL: braces absent | PASS: both braces |
| C matrix and raw relations | not included | Relations PASS individually | FAIL: one matrix row with red literal `\c`; both relations reduced to `ad` | Matrix PASS: two rows, two columns; relations FAIL: reduced to `ad` |

The MathML for A uses a comma operator in each failing cell, versus a 0.167em space in each passing cell. The B passing cells have brace operators and the failing cells do not. For C, the failing display has a single table row and red text `\c`; the fence has two rows of two cells. Both displays omit the raw `<` and `>` expressions in this particular combined input; protected inline renders them separately. This is a focused observation, not evidence that every angle sign fails in a fence: T08's `x<0` renders in its fenced cases. Prefer protected inline for these relation examples, or use separately tested alternatives; inspect each target render. Root cause and a complete minimal contrast for C remain **UNVERIFIED**.

The T09 and T14 PNG fallbacks were inspected separately: their mathematical symbols appear intact. Their header and source caption fit tightly, with T09's title truncated. This is neither a full 22-image review nor an Android app test.

## Observed counterexample · O-2026-10-23-MOBILE-OPERATORNAME

- **Raw observation:** screenshot supplied in conversation shows all six probes in one mobile GitHub-rendered Markdown view: three `\mathrm` controls correctly display upright mathematics, while the three `\operatorname` challenges fail with an explicit forbidden-macro error.
- **Discrimination:** each same-context A/B pair changes the macro while leaving the expression structure fixed; passing controls reject the rival explanation that GitHub math is globally broken on that view.
- **Provenance boundary:** screenshot does not contain full URL, viewed commit, or exact client. Its text matches the reference fixture at `main@da7c846`, but screenshot-to-commit binding remains **UNVERIFIED**. Date is the user-submission date (not embedded on the screen).
- **Independent historical precedent:** [github/markup #1688](https://github.com/github/markup/issues/1688) reports the same message from 2023. It does not establish behavior for all current GitHub surfaces.
- **Portable policy:** avoid `\operatorname` in ordinary GitHub-targeted Markdown; use tested `\mathrm` for simple upright words. Operator spacing and limits are different; review any rewrite for mathematical meaning.
- **Outstanding:** test wiki, Issue/PR comments, desktop operator A/B behavior and other macros. T00–T21 have now been user-reported passing in phone and PC browsers; capture exact client and immutable URL in a follow-up run.
- **Evidence storage:** original screenshot remains in the user conversation and is not publicly hosted in this repo; a redacted screenshot attachment would strengthen independent reproducibility.

## Test-card observation · O-2026-10-23-CARD-PHONE-PC

- **Raw report:** user stated: 'the 22 card renders perfectly on github from my webbrowser on both phone and pc'.
- **Scope:** all T00–T21 test strips in SMPTeX GitHub repository Markdown; **22/22 visually PASS on phone** and **22/22 visually PASS on PC**, according to the same user's report.
- **Provenance:** submitted on 2026-10-23 (America/New_York). The exact viewed commit SHA, browser names/versions, and screenshots of the test card were not supplied. The source link above is a reference fixture, not a verified identification of the viewed revision.
- **Independence boundary:** phone and PC are two viewing environments but may use the same underlying GitHub MathJax renderer. They are not independent implementations.
- **Claim boundary:** a visually successful reference card does not prove semantic correctness, untested macro support or wiki/PR/Issue rendering. The separate mobile `\operatorname` A/B challenge remains a documented FAIL.

## GitHub Android app observation · O-2026-10-23-ANDROID-APP

- **Raw input:** user supplied a scrolling screenshot described as coming from the **GitHub Android app** and explicitly reported the experience as poor. The supplied image is extremely narrow and compressed at 72 × 1536 pixels, which makes the presentation difficult to audit.
- **Distinguishing control:** the same T00–T21 test card was **user-reported 22/22 visually PASS** in both phone and PC **web browsers**. The native Android app and the phone browser are **different rendering/presentation surfaces**.
- **Unresolved mechanism:** the screenshot alone does not isolate an app MathJax bug, viewport/layout CSS failure, long-screenshot stitching, or upload/image downsampling. No individual strip should be marked as a failed TeX render on this evidence.
- **Policy:** **do not use the GitHub Android app as the visual certification reference for SMPTeX**; use the rendered page in a real web browser. Keep app behavior separately marked as an **uncertified / presentation-degraded user report**.
- **Provenance:** screenshot supplied in conversation (not uploaded into this public repository); exact viewed commit, app build number, and screenshot capture parameters are unavailable.

## Context challenges · pinned repository Preview · 2026-11-08 UTC

At approximately 05:31–05:32 UTC, logged-out desktop cloud Chrome (exact version unavailable) viewed the [context challenge file at 76bbf9b49048454ec03752790dd343c4a4ab9edb](https://github.com/femboy2112/SMPTeX/blob/76bbf9b49048454ec03752790dd343c4a4ab9edb/docs/probes/MARKDOWN_CONTEXT_MATRIX.md) in GitHub **repository file Preview**. Screenshots and the DOM, including MathML after typesetting, were inspected. The table reports comparison with each stated expectation; failure is specific to that cell. The file deliberately contains negative challenges, including one that is not valid TeX. No native Android app, Issue/PR comment renderer, or Wiki result follows from these observations.

| Case | Observed outcome |
| --- | --- |
| C1 plain inline; C2 protected inline | **PASS** on both: x with indices 1 and 2 added together equals y with index 1. MathML contains all three subscript nodes. This does not show every Markdown-active expression is safe in plain inline. |
| D1 separated dollar display; D3 fenced control | **PASS**: each shows a equals b as a block. |
| D2 adjacent dollar display | **FAIL**: literal dollar delimiters and a=b remained in a paragraph; there was no math renderer for the cell. |
| E1 standalone equals line | **FAIL**: GitHub made a setext H1 from the opening delimiter and A; B and the closing delimiter remained literal. |
| E2 fenced control | **PASS**: A followed by = B in two MathML table rows. It is a layout control, not an identical source-line contrast. |
| E3 heading-like line | **BLOCKED BEFORE TeX**: the invalid bare parameter-marker challenge became an H1 for B, with literal delimiters, rather than reaching TeX and producing its expected error. This case does not demonstrate a valid TeX formula failing. |
| E4 rule-like line | **FAIL**: the hyphen line became a setext H2 underline and the display split into literal text. |
| E5 list-like line | **FAIL**: the list marker produced a list and the delimiters remained literal. |
| E6 quote-like line | **FAIL**: the quote marker produced a blockquote and the delimiters remained literal. |
| F1 column-zero; F2 two-space indentation | **PASS**: each shows x equals y in display math. |
| F3 list-contained display | **FAIL**: the list contains literal dollar delimiters and x=y; no math renderer appeared for that cell. |
| F4 blockquote-contained display | **PASS**: x equals y appears as display math inside the blockquote. |

E3–E6 have different source tokens and operators, and E3 is deliberately invalid TeX; they are not a matched causal experiment. The separated/adjacent display cases differ in boundary context; E1/E2 differ in line layout as stated in the fixture. Do not extend a cell's verdict to all clients, surfaces, or related syntax.

## SUCC true Wiki matrix contrast · pinned revisions

On 2026-11-08 UTC, logged-out desktop cloud Chrome (version unavailable) also inspected the actual SUCC GitHub Wiki, not a repository directory called wiki. At [The Riemann Connection, revision 84e1ab5495178522aaaf2b3efa4b98e85e8cc3cc](https://github.com/femboy2112/SUCC/wiki/The-Riemann-Connection/84e1ab5495178522aaaf2b3efa4b98e85e8cc3cc), screenshot and post-typesetting MathML showed both intended two-row matrices as single rows of three cells, with a red literal row-spacing command and extra semicolons. At [revision 90e7f4e266915c7de3097c44b4594470524feb06](https://github.com/femboy2112/SUCC/wiki/The-Riemann-Connection/90e7f4e266915c7de3097c44b4594470524feb06), screenshots and MathML showed the symbolic and numeric matrices and the later small matrix as two rows of two cells; the numeric entries are 2, −14, −14, 2, and the determinant −192 is visible. The latest Wiki page history names this latter revision; local Wiki checkout was at ae31f66ad6afd42225f164f5cbce89f6979f6851, and its source at 90e7f4e uses a letter row-break command. Surrounding source and layout also changed across revisions, so this is an observed before/after contrast, not proof that one change alone caused the result or that other Wiki content renders correctly.

## How to change a verdict

1. Open the exact **GitHub-rendered** page at an immutable commit. Log SHA, URL, UTC date, and browser.
2. Compare actual rendered output to expected output for each strip. Note whether a *control* passed before interpreting a challenge failure.
3. Preserve screenshots or a reproducible description. Prefer a minimal passing control and a minimal failing case in the **same** Markdown context.
4. Distinguish SOURCE-CHECKED, VISUALLY OBSERVED, SEMANTICALLY REVIEWED. Use **UNVERIFIED** for a stage that did not run and **AMBIGUOUS** for an observed failure whose mechanism cannot be identified.
5. For wiki/PR/issue rendering, run a new check **on that surface** rather than transferring a repo-page result as proof.

**Important:** a GitHub Markdown API result is not necessarily a complete MathJax browser render. Wiki files live in a separate Git repository and require their own audit.
