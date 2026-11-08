# Matched punctuation and delimiter probe

This is an experiment, not a certification. Compare each expression with its stated expected symbols after GitHub typesetting. Record the immutable URL, surface, browser, date and observed output in the ledger. A repository file is not a Wiki page, and a mobile browser is not the Android app. Do not infer other cells from a pass or failure. These isolated-dollar cases include deliberate render challenges; their TeX is source-checked separately from human visual inspection.

## A: spacing command

Expected: integral from zero to one, x squared followed by a thin space and dx, equals one third. No comma before dx.

Plain inline: $\int_0^1 x^2\,dx=\frac13$.

Protected inline: $`\int_0^1 x^2\,dx=\frac13`$.

Isolated dollar display:

$$
\int_0^1 x^2\,dx=\frac13
$$

Math fence:

```math
\int_0^1 x^2\,dx=\frac13
```

## B: set braces

Expected: a left brace, x in X, a separator, P(x), a right brace, subset-or-equal X.

Plain inline: $\{x\in X\mid P(x)\}\subseteq X$.

Protected inline: $`\{x\in X\mid P(x)\}\subseteq X`$.

Isolated dollar display:

$$
\{x\in X\mid P(x)\}\subseteq X
$$

Math fence:

```math
\{x\in X\mid P(x)\}\subseteq X
```

## C: rows and relation signs

Expected: a two-row, two-column matrix with entries a,b on the first row and c,d on the second; and a < b and c > d. Inspect each symbol and line, not just the absence of an error.

Isolated dollar display:

$$
\begin{pmatrix}a&b\\c&d\end{pmatrix},\quad a<b,\quad c>d
$$

Math fence:

```math
\begin{pmatrix}a&b\\c&d\end{pmatrix},\quad a<b,\quad c>d
```

Protected inline relation: $`a<b`$ and $`c>d`$.
