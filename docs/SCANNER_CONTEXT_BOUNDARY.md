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
