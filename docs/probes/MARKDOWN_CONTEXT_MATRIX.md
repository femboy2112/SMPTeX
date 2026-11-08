# Markdown context challenges

These are **intentional render challenges**, not certified authoring patterns. Inspect the whole rendered GitHub file after typesetting. A heading, missing math, visible delimiters, punctuation, or altered symbol counts as a failure. Each cell has the same stated mathematical intent as its control. The outcomes below are **UNVERIFIED** until recorded for a particular commit, GitHub surface and client. This repository file is not a GitHub Wiki page.

The companion punctuation-context probe covers spacing commands, escaped literal braces, matrix row separators, and raw angle characters across contexts. The cases here cover the other report mechanisms. They are reduced tests of presentation, not mathematical claims.

## C · Markdown-active characters in plain and protected inline

Expect: both forms display two indexed x terms added to an indexed y, with indices 1, 2 and 1.

C1 plain: $x_1 + x_2 = y_1$.

C2 protected: $`x_1 + x_2 = y_1`$.

## D · Display boundaries

Expect: each example displays the same equation on its own line, with a equals b, and no literal dollar signs.

D1 separated:

$$
a=b
$$

D2 adjacent:
$$
a=b
$$
Text immediately follows this display.

D3 fenced control:

```math
a=b
```

## E · Markdown-active display lines

Expect: each case displays A, =, and B in that order; the equals line is not a heading. The control uses two aligned rows, while E1 presents the tokens on three source lines.

E1 dollar display:

$$
A
=
B
$$

E2 fenced control:

```math
\begin{aligned}
A \\
= B
\end{aligned}
```

The next challenges are intentionally constructed to reveal Markdown block interpretation. E4–E6 use the same variables as E1/E2 but differ in operator and layout; inspect whether Markdown splits or swallows content. **E3 is deliberately invalid TeX** (a bare parameter marker), so its expected outcome is a TeX error if it reaches the renderer; it tests whether Markdown instead makes a heading. Passing the lightweight source check does not validate that TeX.

E3 heading-like line:

$$
A
# B
$$

E4 rule-like line:

$$
A
---
B
$$

E5 list-like line:

$$
A
- B
$$

E6 quote-like line:

$$
A
> B
$$

## F · Indentation and containers

Expect: each display contains x equals y, with no visible dollar signs. The list cases remain inside the list, and the quote case inside the quotation.

F1 column-zero control:

$$
x=y
$$

F2 two-space indentation:

  $$
  x=y
  $$

F3 list with blank lines:

- List item.

  $$
  x=y
  $$

  Continuation.

F4 blockquote with blank lines:

> Quote.
>
> $$
> x=y
> $$
>
> Continuation.
