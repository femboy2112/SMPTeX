#!/usr/bin/env python3
"""Source-matched MathJax PNG snapshots for native GitHub Markdown viewing."""
from __future__ import annotations
import argparse, hashlib, io, json, re, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CARD=ROOT/"docs/GITHUB_MATH_TEST_CARD.md"
MANIFEST=ROOT/"assets/mobile/manifest.json"
HEAD=re.compile(r"^## (T\d\d) · (.+)$",re.M)
FENCE=re.compile(r"^\x60{3}math\s*\n(.*?)\n\x60{3}",re.M|re.S)
DISPLAY=re.compile(r"^\$\$\s*\n(.*?)\n\$\$",re.M|re.S)
PROTECTED=re.compile(r"\$\x60([^\n]+?)\x60\$")
INLINE=re.compile(r"(?<!\$)\$(?!\$|\x60)([^\n$]+?)\$(?!\$)")
PNG_HEADER=b"\x89PNG\r\n\x1a\n"

def strips(text):
    markers=list(HEAD.finditer(text));result=[]
    for i,match in enumerate(markers):
        body=text[match.end():markers[i+1].start() if i+1<len(markers) else len(text)]
        body=re.split(r"^\s*---\s*$|^## ",body,maxsplit=1,flags=re.M)[0]
        expr=[]
        for rule in (FENCE,DISPLAY,PROTECTED):
            body=rule.sub(lambda m:(expr.append(m.group(1).strip()) or "\n"),body)
        body=re.sub(r"<span>\$</span>","",body)
        body=re.sub(r"\x60[^\x60\n]*\x60","",body)
        expr += [m.group(1).strip() for m in INLINE.finditer(body)]
        if not expr:raise ValueError("Missing live TeX in "+match.group(1))
        result.append({"id":match.group(1),"title":match.group(2),"tex":expr})
    if [x["id"] for x in result]!=[f"T{i:02}" for i in range(22)]:
        raise ValueError("Expected T00 through T21, in order")
    return result

def digest(parts):
    return hashlib.sha256(json.dumps(parts,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def mobile_lines(source):
    # Reflow only known T00–T21 samples at presentation spacing boundaries.
    return [part.strip() for part in source.split(r"\qquad") if part.strip()]

def check():
    values=strips(CARD.read_text(encoding="utf-8"))
    if not MANIFEST.is_file():
        print("PNG manifest not yet generated",file=sys.stderr)
        return 1
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    found={entry["id"]:entry for entry in manifest["entries"]}
    errors=[]
    for value in values:
        ident=value["id"];record=found.get(ident)
        if record is None:errors.append(ident+" missing record");continue
        if record["tex_sha256"]!=digest(value["tex"]):errors.append(ident+" source drift")
        asset=ROOT/record["path"]
        if not asset.exists():errors.append(ident+" image missing");continue
        raw=asset.read_bytes()
        if not raw.startswith(PNG_HEADER) or hashlib.sha256(raw).hexdigest()!=record["png_sha256"]:
            errors.append(ident+" corrupted / stale image")
    if len(found)!=22:errors.append("manifest must contain exactly 22 records")
    for error in errors:print("ERROR",error,file=sys.stderr)
    print(f"SMPTeX mobile images: {len(values)} strips, {len(errors)} findings")
    return int(bool(errors))

def build():
    try:
        import cairosvg
        from PIL import Image,ImageDraw,ImageFont
    except ImportError as err:
        print("Missing optional Pillow/CairoSVG: "+str(err),file=sys.stderr);return 2
    values=strips(CARD.read_text(encoding="utf-8"))
    formulas=[segment for strip in values for item in strip["tex"] for segment in mobile_lines(item)]
    run=subprocess.run(["node",str(ROOT/"scripts/render_mathjax_svg.cjs")],
        input=json.dumps({"tex":formulas}),text=True,capture_output=True,check=False)
    if run.returncode:print(run.stderr,file=sys.stderr);return 2
    svgs=json.loads(run.stdout)["svg"]
    if len(svgs)!=len(formulas):raise ValueError("SVG count mismatch")
    try:
        regular=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
        bold=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",32)
    except OSError:regular=ImageFont.load_default();bold=regular
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    records=[];index=0
    for entry in values:
        pictures=[]
        for formula in entry["tex"]:
            for segment in mobile_lines(formula):
                png=cairosvg.svg2png(bytestring=svgs[index].encode("utf-8"),scale=3)
                index+=1
                pic=Image.open(io.BytesIO(png)).convert("RGBA")
                if pic.width<10 or pic.height<10:raise ValueError("Empty formula "+entry["id"])
                pictures.append(pic)
        width=max(800,max(pic.width for pic in pictures)+90)
        height=140+sum(max(86,pic.height)+22 for pic in pictures)
        canvas=Image.new("RGB",(width,height),"#f7f7f4")
        draw=ImageDraw.Draw(canvas)
        draw.rectangle((0,0,width-1,height-1),outline="#9fa0a5",width=2)
        draw.rectangle((0,0,14,height-1),fill="#13131a")
        headline=entry["id"]+"  "+entry["title"];original=headline
        while len(headline)>4 and draw.textlength(headline,font=bold)>width-100:
            headline=headline[:-2]
        if headline!=original:headline=headline.rstrip()+"…"
        draw.text((42,22),headline,font=bold,fill="#17171c")
        draw.text((44,68),"REFERENCE IMAGE  ·  SOURCE: GITHUB_MATH_TEST_CARD.md",font=regular,fill="#55565e")
        y=118
        for pic in pictures:
            canvas.paste(pic,(45,y+max(0,(max(86,pic.height)-pic.height)//2)),pic)
            y+=max(86,pic.height)+22
        target=MANIFEST.parent/(entry["id"].lower()+".png")
        canvas.save(target,optimize=True)
        records.append({"id":entry["id"],"title":entry["title"],
           "tex_sha256":digest(entry["tex"]),
           "path":target.relative_to(ROOT).as_posix(),
           "png_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
           "width":width,"height":height})
    MANIFEST.write_text(json.dumps({"version":1,"source":"docs/GITHUB_MATH_TEST_CARD.md",
        "renderer":"MathJax 3 SVG -> CairoSVG/Pillow PNG",
        "scope":"Static reference, not native GitHub Android math certification",
        "entries":records},indent=2)+"\n",encoding="utf-8")
    return check()

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build",action="store_true",help="Generate all 22 PNGs")
    args=p.parse_args()
    raise SystemExit(build() if args.build else check())
