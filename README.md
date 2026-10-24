![SMPTeX broadcast test pattern: PLEASE STAND BY — MATHJAX FAILURE](assets/smptex-test-pattern.svg)

# SMPTeX 📺

**Society for Markdown Parsing and TeXorcism** · *Some Math Probably Typesets Eventually™*

**A calibration test card for GitHub mathematics.** Make Claude, Codex, and other coding agents prove their Markdown math is *source-valid*, then verify how it actually renders on GitHub. The broadcast bars are a joke; the test suite is not.

[**🧪 Open the live math test card**](docs/GITHUB_MATH_TEST_CARD.md) · [**🔍 Inspect the `\operatorname` A/B probe**](docs/probes/OPERATORNAME_AB.md) · [**📋 Rendering review checklist**](docs/RENDER_REVIEW_CHECKLIST.md) · [**📒 Compatibility ledger**](docs/MATH_COMPATIBILITY_LEDGER.md)

## Why this exists

Mathematically valid TeX can still produce broken GitHub Markdown. A local parser, an upstream macro list, and GitHub's rendered page answer **different questions**. SMPTeX deliberately keeps those observations separate:

| Channel | What it tells us | What it does **not** establish |
| --- | --- | --- |
| **Source preflight** | Known delimiter, brace, environment, and macro-policy errors | Visual rendering correctness |
| **Live test card** | What GitHub actually displays in the current context | Mathematical correctness of every expression |
| **Semantic review** | Whether the rendered expression says what the author intended | Rendering portability to other surfaces |

## Start calibration

1. Open the [test card](docs/GITHUB_MATH_TEST_CARD.md) **in GitHub's rendered view**, not the Raw tab. Compare strips T00–T21 against their expectations.
2. Open the [operator A/B probe](docs/probes/OPERATORNAME_AB.md). It **really renders both variants**; the challenge is not hidden in a code sample.
3. Record outcomes, exact URLs, commit SHA, and surface in the [ledger](docs/MATH_COMPATIBILITY_LEDGER.md). Use the [checklist](docs/RENDER_REVIEW_CHECKLIST.md) or [file a rendering regression](https://github.com/femboy2112/SMPTeX/issues/new?template=render-regression.md).
4. Run the local checks (Python 3.10+, standard library only):

```bash
python -m unittest discover -s tests -v
python scripts/math_guard.py . --strict-portable --exclude docs/probes/OPERATORNAME_AB.md
python scripts/math_guard.py docs/probes/OPERATORNAME_AB.md
```

The experimental probe is **intentionally exempt from the strict macro-policy check**, but it still passes the non-strict source checker; this lets us test a disputed command without teaching agents to use it in ordinary documents.

## Install the math contract in another repository

- Follow [agent installation instructions](INSTALLATION_PROMPT.md), preserving that repository's existing rules and branch history.
- Copy the guard, tests, workflow, and reference documents; customize the workflow to match existing CI.
- Make sure `AGENTS.md` and/or `CLAUDE.md` point to the [portable authoring contract](AGENTS_MATH_PROTOCOL.md).
- Use a feature branch and visually review **new** macros in the target GitHub repo or wiki before declaring them supported.

This repository itself ships with [`AGENTS.md`](AGENTS.md) and [`CLAUDE.md`](CLAUDE.md).

## What passes and what remains uncertain?

The guard runs locally without nonstdlib dependencies; its test suite includes both valid examples and deliberately broken mutations. **Passing CI is not visual certification.** Human GitHub browser inspection is still required; see the [current evidence ledger](docs/MATH_COMPATIBILITY_LEDGER.md). In the **2026-10-23 mobile repository-Markdown A/B screenshot**, `\mathrm` passed in all three contexts, while `\operatorname` produced GitHub's explicit **"The following macros are not allowed: operatorname"** error in inline, display, and `math`-fence contexts. This is an observation on the tested surface, not a universal MathJax incompatibility. [See the evidence ledger](docs/MATH_COMPATIBILITY_LEDGER.md). All T00–T21 strips and other GitHub surfaces remain unverified.

**Reference specifications:** [GitHub's official mathematical expressions guide](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions) · [MathJax supported TeX commands](https://docs.mathjax.org/en/stable/input/tex/macros/)

---

*WE ARE EXPERIENCING TECHNICAL DIFFICULTIES. Your regularly scheduled mathematics will resume once Claude remembers how dollar signs work.* 💀