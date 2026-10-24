# SMPTeX agent contract

Applies to the full repository. Read [AGENTS_MATH_PROTOCOL.md](AGENTS_MATH_PROTOCOL.md) before editing mathematics or math-bearing Markdown; its rules are binding unless the task explicitly changes the calibration policy.

## Working discipline

- Inspect actual branch, HEAD, local changes, and relevant repo instructions. Don't overwrite user modifications or silently replace existing math definitions.
- Keep technical claims separated as **DOCUMENTED**, **SOURCE-CHECKED**, **VISUALLY OBSERVED**, **SEMANTICALLY VERIFIED**, or **UNVERIFIED**. Do not describe a source lint as a browser render.
- The reference [test card](docs/GITHUB_MATH_TEST_CARD.md) uses 22 candidate test strips. A reader must review their *GitHub-rendered* output.
- [The operator probe](docs/probes/OPERATORNAME_AB.md) deliberately tests a disputed macro. Preserve the experiment and its scope. Never apply a failure conclusion to every MathJax installation without evidence.
- GitHub document math is a source-format problem plus a rendering problem. Don't claim mathematical proof merely because a symbol displayed correctly.
- **Do not treat the GitHub Android app as a reference renderer.** T00–T21 were user-reported to pass in phone/PC browsers; the user supplied a poor Android-app capture, but its mechanism and strip-level failures are unresolved. Inspect with a web browser and keep app presentation observations distinct from mathematical or source failures. See [the ledger](docs/MATH_COMPATIBILITY_LEDGER.md).

- Keep the [mobile image fallback](docs/MOBILE_APP_FALLBACK.md) derived from the 22 live math strips; after generated images exist, `python scripts/mobile_fallback.py` must validate source/image SHA-256 checksums. Static images are *never* a MathJax browser certification.

## Checks before pushing math changes

```bash
python -m unittest discover -s tests -v
python scripts/math_guard.py . --strict-portable --exclude docs/probes/OPERATORNAME_AB.md
python scripts/math_guard.py docs/probes/OPERATORNAME_AB.md
```

The source guard intentionally excludes **only the named probe** from strict portability. The second check still lints it for malformed math source. All other math-bearing Markdown must obey the conservative authoring policy.

When GitHub rendering is not available, log visual outcomes **UNVERIFIED**. Do not manufacture screenshots, CI results, macro support, or user confirmations. Use path-filtered CI; no unrelated build churn.
