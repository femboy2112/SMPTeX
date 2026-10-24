"""Positive, negative, and mutation controls for the SMPTeX image fallback."""
import importlib.util,sys,unittest
from pathlib import Path
script=Path(__file__).resolve().parents[1]/"scripts/mobile_fallback.py"
spec=importlib.util.spec_from_file_location("mobile_fallback",script)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class MobileFallbackTests(unittest.TestCase):
 def test_exactly_22_live_strips(self):
  samples=m.strips(m.CARD.read_text(encoding="utf-8"))
  self.assertEqual([s["id"] for s in samples],[f"T{i:02}" for i in range(22)])
  self.assertEqual(samples[0]["tex"],["x^2 + y^2 = z^2"])
  self.assertEqual(samples[19]["tex"],["100/2=50"])
  self.assertEqual(len(samples[21]["tex"]),2)
 def test_missing_live_math(self):
  src=m.CARD.read_text(encoding="utf-8").replace(
   "A basic invariant: $x^2 + y^2 = z^2$.","A basic invariant: no math.")
  with self.assertRaisesRegex(ValueError,"T00"):m.strips(src)
 def test_bad_strip_number(self):
  src=m.CARD.read_text(encoding="utf-8").replace("## T21 ·","## T99 ·")
  with self.assertRaises(ValueError):m.strips(src)
 def test_digest_mutation(self):
  self.assertNotEqual(m.digest(["x^2"]),m.digest(["x^3"]))
 def test_png_integrity(self):
  if not m.MANIFEST.is_file():
   self.skipTest("One-time snapshot generator has not yet committed assets")
  self.assertEqual(m.check(),0)
if __name__=="__main__":unittest.main()
