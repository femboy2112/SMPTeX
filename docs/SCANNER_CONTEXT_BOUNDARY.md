# Scanner context boundary

The guard recognizes GFM table headers followed by a matching delimiter row,
including tables without outer pipes, and warns about unescaped pipes within
math in those tables. It does not infer tables from pipe-leading prose. It
ignores fenced code, indented code, inline and multiline code spans, and HTML
comments in supported contexts; a fence labelled `math` is checked instead.
Backtick fence info strings containing a backtick are not fence openers.
Block quotes with explicit markers and simple list-item indentation are handled;
a block quote inside a list emits `UNSUPPORTED_CONTAINER` for manual inspection.
Complex nested or lazy containers, tabs in container prefixes, HTML block types
other than comments, and the full CommonMark block parsing algorithm are outside
this lightweight scanner. Recognized HTML block openers produce an explicit
manual-inspection finding. Check complicated Markdown at its rendered target.
The scanner reports an unterminated fence even where Markdown closes it at the
end of a containing block; it does not let such a block consume later content.

The TeX checks recognize control words and symbols, simple environment names,
comments, braces, and ordering of paired delimiters. They are not a TeX parser.
An environment argument separated from its command by a comment may be flagged
conservatively even though TeX accepts it. A source pass establishes neither
rendering fidelity nor mathematical correctness.

Syntax references: [GFM tables](https://github.github.com/gfm/#tables-extension-)
and [CommonMark fenced code](https://spec.commonmark.org/0.31.2/#fenced-code-blocks).

## Opt-in repository Preview checks

The default `source` profile checks source only and retains existing behavior.
`--profile repository-preview` adds conservative diagnostics based on the
matched [punctuation experiment](https://github.com/femboy2112/SMPTeX/blob/1918795de676db953cc1d4e720a984ceeef2c51a/docs/probes/PUNCTUATION_CONTEXT.md)
on desktop Chrome repository file Preview. Plain inline and isolated dollar
displays showed thin spaces as commas and lost escaped literal braces; their
protected-inline and fenced counterparts passed. A matrix row separator in the
isolated-dollar example failed, while its fenced counterpart passed. These
findings prompt review; they do not assert that every occurrence fails, that
Markdown or TeX forbids the source, or that other clients behave the same.
The diagnostics leave protected inline and math fences unchanged. They cannot
certify rendering. JSON output reports the selected profile. No profile is
inferred from a path, and Wiki, issue, PR, mobile browser, and native-app
behavior remains unverified by this probe. For an intentionally negative
fixture, run the default source check separately; do not treat an opt-in
repository Preview finding as invalid TeX.

The profile also marks dollar displays adjacent to nonblank lines, containing
standalone equals or hyphen-rule lines, list/quote/heading-like content, or placed
in a list. These are review prompts from the
[repository Preview context challenges](https://github.com/femboy2112/SMPTeX/blob/76bbf9b49048454ec03752790dd343c4a4ab9edb/docs/probes/MARKDOWN_CONTEXT_MATRIX.md),
not a blanket claim that every such use fails. The heading-like challenge was
invalid TeX and does not establish a valid formula failing. Separate blank
lines, a two-space indented display, a fenced control and a quoted display
passed in that particular observation. Wiki and other surfaces are not inferred.
