# P00–P05 · `\operatorname` Live A/B Probe

[← Back to SMPTeX](../../README.md) · [← Test card](../GITHUB_MATH_TEST_CARD.md) · [Record evidence](../MATH_COMPATIBILITY_LEDGER.md)

**Question:** does GitHub actually render the MathJax macro `\operatorname` in each of the supported Markdown math contexts?

**Do not infer the answer from source syntax alone.** Upstream MathJax documents the macro; GitHub's exact rendering environment is the subject of this probe. Below are **live mathematics**, not escaped code samples. The command is blocked in ordinary strict-portable docs until its behavior is observed and recorded.

## P00 · Inline control: `\mathrm`

The control is $\mathrm{rank}(A)=2$.

**Expected:** upright 'rank' beside the mathematical symbol A.

## P01 · Inline challenge: `\operatorname`

The challenge is $\operatorname{rank}(A)=2$.

**Compare:** does it render as an upright operator with appropriate spacing, or produce raw TeX / an error?

## P02 · Display control: `\mathrm`

$$
\mathrm{rank}(A)=2
$$

## P03 · Display challenge: `\operatorname`

$$
\operatorname{rank}(A)=2
$$

## P04 · Math fence control

```math
\mathrm{rank}(A)=2
```

## P05 · Math fence challenge

```math
\operatorname{rank}(A)=2
```

## Inspection report

| Check | Visual status | Evidence |
| --- | --- | --- |
| P00 inline control | UNVERIFIED | — |
| P01 inline challenge | UNVERIFIED | — |
| P02 display control | UNVERIFIED | — |
| P03 display challenge | UNVERIFIED | — |
| P04 math-fence control | UNVERIFIED | — |
| P05 math-fence challenge | UNVERIFIED | — |

Record date, GitHub URL, commit SHA, and whether you were looking at repository Markdown, a wiki, or a PR in the [compatibility ledger](../MATH_COMPATIBILITY_LEDGER.md). **Control failure means the challenge cannot isolate macro support**. No screenshot = no visual claim.
