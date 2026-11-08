#!/usr/bin/env python3
"""Generate and validate in disposable space without changing committed images."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="smptex-generation-") as tmp:
    output = Path(tmp)
    (output / "docs").mkdir()
    for name in ("GITHUB_MATH_TEST_CARD.md", "MOBILE_APP_FALLBACK.md"):
        shutil.copy2(root / "docs" / name, output / "docs" / name)
    subprocess.run([sys.executable, str(root / "scripts/mobile_fallback.py"), "--build", "--output-root", str(output)], check=True, timeout=180)
    card=output / "docs" / "GITHUB_MATH_TEST_CARD.md"
    original=card.read_text(encoding="utf-8")
    altered=original.replace("$x^2 + y^2 = z^2$", "$x^3 + y^3 = z^3$", 1)
    if altered==original: raise SystemExit("output-root source mutation control missing")
    card.write_text(altered, encoding="utf-8")
    # A build reading the repository card instead of this card fails validation.
    subprocess.run([sys.executable, str(root / "scripts/mobile_fallback.py"), "--build", "--output-root", str(output)], check=True, timeout=180)

# An unknown command must surface as a renderer error, not literal red text.
probe = subprocess.run(["node", str(root / "scripts/render_mathjax_svg.cjs")],
    input=json.dumps({"tex": [r"\definitelynotacommand{x}"]}),
    text=True, capture_output=True, timeout=30)
if probe.returncode == 0:
    raise SystemExit("renderer accepted unknown TeX command")
