# Claude instructions for SMPTeX

Follow [AGENTS.md](AGENTS.md) and [AGENTS_MATH_PROTOCOL.md](AGENTS_MATH_PROTOCOL.md). Before changing calibration behavior, run the existing positive, negative, and mutation controls; add a fixture for every new bug class.

Remember the distinction: **source pass ≠ browser render ≠ semantic proof**. The `\operatorname` comparison in `docs/probes/OPERATORNAME_AB.md` is a **real rendered experiment**, not an invitation to claim a verdict without looking at GitHub.

For changed repository Markdown, the optional `--profile repository-preview`
adds conservative, context-specific review findings. The default is `source`;
JSON includes the selected profile. An intentional render challenge can
correctly produce a profile finding while passing its separate source check.
Inspect the actual target and preserve operator spacing and meaning. Neither
profile certifies Wiki or native-app rendering; see the ledger and scanner
boundary for observed cases and limits.
