"""Positive, negative, and mutation controls for the SMPTeX image fallback."""
import importlib.util,sys,unittest,tempfile,shutil,json,hashlib,contextlib,io
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
  self.assertEqual(m.check(),0)
 def test_artifact_mutations(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for name in ("docs/GITHUB_MATH_TEST_CARD.md","docs/MOBILE_APP_FALLBACK.md","assets/mobile"):
    src=m.ROOT/name; dst=root/name
    if src.is_dir(): shutil.copytree(src,dst)
    else: dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
   man=root/"assets/mobile/manifest.json"; original=man.read_text(); data=json.loads(original)
   def fails():
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(m.check(root),1)
   with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(m.check(root),0)
   man.unlink(); fails(); man.write_text(original)
   for mutate in (lambda x:x["entries"].append(x["entries"][0]),
                  lambda x:x["entries"][0].update(id="T99"),
                  lambda x:x["entries"].__setitem__(0,{}),
                  lambda x:x["entries"][0].update(tex_sha256="0"*64),
                  lambda x:x["entries"][0].update(path="../outside.png")):
    x=json.loads(original); mutate(x); man.write_text(json.dumps(x)); fails()
   man.write_text(original)
   card=root/"docs/GITHUB_MATH_TEST_CARD.md"; card_original=card.read_text()
   card.write_text("<!--\n"+card_original+"\n-->"); fails()
   card.write_text("```text\n"+card_original+"\n```"); fails()
   card.write_text(card_original)
   first=r"| Divisibility | $a\mid b$ | The vertical relation should remain inside this cell |"
   second=r"| Conditional probability | $P(A\mid B)$ | The conditional separator should stay inside its cell |"
   changed=card_original.replace(first+"\n"+second,second+"\n"+first.replace(r"$a\mid b$",r"$`a\mid b`$"))
   self.assertNotEqual(changed,card_original)
   card.write_text(changed); fails(); card.write_text(card_original)
   live="$x^2 + y^2 = z^2$"
   for hidden in ("<!-- "+live+" -->", "`"+live+"`", "<div>"+live+"</div>", "\n```text\n"+live+"\n```\n", "\n    "+live+"\n", "`before\n"+live+"\nafter`"):
    self.assertIn(live,card_original)
    card.write_text(card_original.replace(live,hidden,1)); fails()
   card.write_text(card_original)
   doc=root/"docs/MOBILE_APP_FALLBACK.md"; doc_original=doc.read_text()
   doc.write_text("<!--\n"+doc_original+"\n-->"); fails()
   doc.write_text(doc_original.replace("## 22 reference images", "## 22 reference images\n\n```" ).replace("## Validation and rebuilding", "```\n\n## Validation and rebuilding")); fails()
   doc.write_text(doc_original)
   image=root/data["entries"][0]["path"]; old=image.read_bytes(); image.unlink(); fails()
   image.write_bytes(old+b"x"); fails()
   image.write_bytes(m.PNG_HEADER); x=json.loads(original); x["entries"][0]["png_sha256"]=hashlib.sha256(m.PNG_HEADER).hexdigest(); man.write_text(json.dumps(x)); fails()
   image.write_bytes(old); man.write_text(original)
   image.rename(image.with_name("renamed.png")); data["entries"][0]["path"]="assets/mobile/renamed.png"; man.write_text(json.dumps(data)); fails()
if __name__=="__main__":unittest.main()
