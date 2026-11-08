#!/usr/bin/env python3
"""Source-matched MathJax PNG snapshots for native GitHub Markdown viewing."""
from __future__ import annotations
import argparse, hashlib, io, json, re, subprocess, sys, struct, zlib, shutil
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
    if "<!--" in text or "-->" in text:
        raise ValueError("HTML comments are not permitted in the reference card")
    if markers and ("<" in text[:markers[0].start()] or "`" in text[:markers[0].start()] or re.search(r"^ {0,3}~{3,}",text[:markers[0].start()],re.M)):
        raise ValueError("reference card preamble cannot contain HTML or code fences")
    for i,match in enumerate(markers):
        body=text[match.end():markers[i+1].start() if i+1<len(markers) else len(text)]
        if i+1==len(markers):
            body=re.split(r"^\s*---\s*$|^## ",body,maxsplit=1,flags=re.M)[0]
        # Narrow reference-card contract: comments and raw HTML can hide live
        # content. Only the existing literal-dollar span is permitted. This is
        # intentionally not a general Markdown parser.
        if "<!--" in body or "-->" in body:
            raise ValueError("HTML comments are not permitted in "+match.group(1))
        found=[]
        def mask(token):
            return re.sub(r"[^\n]", " ", token.group(0))
        for rule in (FENCE,DISPLAY):
            def capture(token):
                found.append((token.start(),token.group(1).strip()))
                return mask(token)
            body=rule.sub(capture,body)
        body=re.sub(r"<span>\$</span>",mask,body)
        if re.search(r"^ {0,3}(?:`{3,}|~{3,})|^(?: {4,}|\t)\S|^ {0,3}>",body,re.M):
            raise ValueError("unsupported fenced, indented, or quoted content in "+match.group(1))
        # Recognize protected math and literal code together from left to right.
        # Exact backtick run matching keeps math inside a code span opaque.
        token_re=re.compile(r"(?P<protected>\$`(?P<tex>[^\n]+?)`\$)|(?<!`)(?P<ticks>`+)(?!`)(?P<code>[\s\S]*?)(?<!`)(?P=ticks)(?!`)")
        def inline_token(token):
            if token.group("protected") is not None:
                found.append((token.start(),token.group("tex").strip()))
            elif "\n" in token.group("code"):
                raise ValueError("multiline code span is not supported in "+match.group(1))
            return mask(token)
        body=token_re.sub(inline_token,body)
        # Ignore literal code and math before looking for HTML block starts.
        # Plain inline math is masked after its positions are collected below.
        for token in INLINE.finditer(body): found.append((token.start(),token.group(1).strip()))
        body=INLINE.sub(mask,body)
        if re.search(r"<[A-Za-z!/?]",body):
            raise ValueError("raw HTML is not permitted in "+match.group(1))
        expr=[tex for _,tex in sorted(found)]
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

def png_dimensions(raw):
    """Validate the bounded RGB PNG format emitted by this builder, including CRC and pixels."""
    if not raw.startswith(PNG_HEADER): raise ValueError("invalid PNG signature")
    pos=8; chunks=[]; pixels=b""; dims=None
    while pos < len(raw):
        if pos+12>len(raw): raise ValueError("truncated PNG chunk")
        length=struct.unpack(">I",raw[pos:pos+4])[0]
        end=pos+12+length
        if end>len(raw): raise ValueError("truncated PNG chunk data")
        kind=raw[pos+4:pos+8]; data=raw[pos+8:pos+8+length]
        if zlib.crc32(kind+data)&0xffffffff != struct.unpack(">I",raw[pos+8+length:end])[0]:
            raise ValueError("PNG chunk checksum mismatch")
        chunks.append(kind)
        if kind==b"IHDR":
            if len(chunks)!=1 or len(data)!=13: raise ValueError("bad IHDR")
            w,h,depth,color,comp,flt,interlace=struct.unpack(">IIBBBBB",data)
            if not (1<=w<=10000 and 1<=h<=10000 and depth==8 and color==2 and comp==flt==interlace==0):
                raise ValueError("unsupported PNG format or dimensions")
            dims=(w,h)
        elif kind==b"IDAT": pixels+=data
        elif kind==b"IEND":
            if data or end!=len(raw): raise ValueError("invalid IEND")
            break
        pos=end
    if dims is None or chunks.count(b"IHDR")!=1 or chunks.count(b"IEND")!=1 or b"IDAT" not in chunks or chunks[-1]!=b"IEND":
        raise ValueError("missing required PNG chunks")
    w,h=dims; expected=(3*w+1)*h
    dec=zlib.decompressobj(); raw_pixels=dec.decompress(pixels,expected+1)
    if len(raw_pixels)!=expected or not dec.eof or dec.unused_data or dec.unconsumed_tail:
        raise ValueError("invalid compressed PNG pixels")
    if any(raw_pixels[i*(3*w+1)]>4 for i in range(h)): raise ValueError("invalid PNG row filter")
    return dims

def check(root=ROOT):
    errors=[]
    try:
        values=strips((root/"docs/GITHUB_MATH_TEST_CARD.md").read_text(encoding="utf-8"))
        manifest=json.loads((root/"assets/mobile/manifest.json").read_text(encoding="utf-8"))
        if not isinstance(manifest,dict) or type(manifest.get("version")) is not int or manifest["version"]!=1 or manifest.get("source")!="docs/GITHUB_MATH_TEST_CARD.md":
            raise ValueError("invalid manifest version or source")
        records=manifest.get("entries")
        if not isinstance(records,list) or len(records)!=22: raise ValueError("manifest must contain exactly 22 records")
        ids=[]; paths=[]
        for rec in records:
            if not isinstance(rec,dict): raise ValueError("manifest record must be an object")
            if not all(isinstance(rec.get(k),str) for k in ("id","title","path","tex_sha256","png_sha256")) or not all(type(rec.get(k)) is int and rec[k]>0 for k in ("width","height")):
                raise ValueError("manifest record has missing or invalid fields")
            if not all(re.fullmatch(r"[0-9a-f]{64}",rec[k]) for k in ("tex_sha256","png_sha256")): raise ValueError("invalid SHA-256")
            path=rec["path"]
            if not re.fullmatch(r"assets/mobile/[a-zA-Z0-9_-]+\.png",path) or not (root/path).resolve().is_relative_to(root.resolve()): raise ValueError("unsafe image path")
            ids.append(rec["id"]); paths.append(path)
        if len(set(ids))!=22 or set(ids)!={f"T{i:02}" for i in range(22)}: raise ValueError("duplicate, missing or unknown IDs")
        if len(set(paths))!=22: raise ValueError("duplicate image paths")
        found={x["id"]:x for x in records}
        document=(root/"docs/MOBILE_APP_FALLBACK.md").read_text(encoding="utf-8")
        # The reference section has a deliberately narrow, auditable syntax:
        # exactly one heading and image paragraph per card, in source order.
        # This rejects hidden links in HTML comments, fences, and other containers.
        header="## 22 reference images"
        if document.count(header)!=1: raise ValueError("missing or duplicate fallback reference section")
        before,section=document.split(header,1)
        if "<" in before or "`" in before or re.search(r"^ {0,3}~{3,}", before, re.M):
            raise ValueError("fallback preamble must not contain HTML, code spans, or fences")
        section=re.split(r"^## ",section,maxsplit=1,flags=re.M)[0]
        lines=[line for line in section.splitlines() if line.strip()]
        expected_lines=[]
        for value in values:
            rec=found[value["id"]]
            expected_lines.extend(["### "+value["id"]+" · "+value["title"],
                "!["+value["id"]+" MathJax-rendered reference](../"+rec["path"]+")"])
        if lines!=expected_lines: errors.append("fallback reference section headings or live image links mismatch")
        for value in values:
            ident=value["id"]; rec=found[ident]
            if rec["title"]!=value["title"] or rec["tex_sha256"]!=digest(value["tex"]): errors.append(ident+" source drift")
            try:
                raw=(root/rec["path"]).read_bytes()
                if hashlib.sha256(raw).hexdigest()!=rec["png_sha256"]: errors.append(ident+" image digest mismatch")
                if png_dimensions(raw)!=(rec["width"],rec["height"]): errors.append(ident+" image dimensions mismatch")
            except (OSError,ValueError,zlib.error) as err: errors.append(ident+" image invalid: "+str(err))
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as err:
        errors.append(str(err))
    for error in errors: print("ERROR",error,file=sys.stderr)
    print(f"SMPTeX mobile images: {len(errors)} findings")
    return int(bool(errors))

def build(output_root=ROOT):
    try:
        import cairosvg
        from PIL import Image,ImageDraw,ImageFont
    except ImportError as err:
        print("Missing optional Pillow/CairoSVG: "+str(err),file=sys.stderr);return 2
    values=strips((output_root/"docs/GITHUB_MATH_TEST_CARD.md").read_text(encoding="utf-8"))
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
    manifest_path=output_root/"assets/mobile/manifest.json"
    manifest_path.parent.mkdir(parents=True,exist_ok=True)
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
        headline=entry["id"]+"  "+entry["title"]
        headline_font=bold
        if draw.textlength(headline,font=headline_font)>width-100:
            try:
                for size in range(31,15,-1):
                    headline_font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",size)
                    if draw.textlength(headline,font=headline_font)<=width-100: break
            except OSError:
                headline_font=ImageFont.load_default()
        if draw.textlength(headline,font=headline_font)>width-100:
            raise ValueError("Reference title does not fit "+entry["id"])
        draw.text((42,22),headline,font=headline_font,fill="#17171c")
        # Fit the provenance caption within the border at narrow card widths.
        caption="REFERENCE IMAGE  ·  SOURCE: GITHUB_MATH_TEST_CARD.md"
        caption_font=regular
        if draw.textlength(caption,font=caption_font)>width-100:
            try:
                for size in range(23,9,-1):
                    caption_font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",size)
                    if draw.textlength(caption,font=caption_font)<=width-100: break
            except OSError:
                caption_font=ImageFont.load_default()
        if draw.textlength(caption,font=caption_font)>width-100:
            raise ValueError("Reference caption does not fit "+entry["id"])
        draw.text((44,68),caption,font=caption_font,fill="#55565e")
        y=118
        for pic in pictures:
            canvas.paste(pic,(45,y+max(0,(max(86,pic.height)-pic.height)//2)),pic)
            y+=max(86,pic.height)+22
        target=manifest_path.parent/(entry["id"].lower()+".png")
        canvas.save(target,optimize=True)
        records.append({"id":entry["id"],"title":entry["title"],
           "tex_sha256":digest(entry["tex"]),
           "path":target.relative_to(output_root).as_posix(),
           "png_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
           "width":width,"height":height})
    manifest_path.write_text(json.dumps({"version":1,"source":"docs/GITHUB_MATH_TEST_CARD.md",
        "renderer":"MathJax 3 SVG -> CairoSVG/Pillow PNG",
        "scope":"Static reference, not native GitHub Android math certification",
        "entries":records},indent=2)+"\n",encoding="utf-8")
    return check(output_root)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build",action="store_true",help="Generate all 22 PNGs")
    p.add_argument("--output-root",type=Path,help="Disposable root for generation (must contain docs inputs)")
    args=p.parse_args()
    if args.output_root and not args.build: p.error("--output-root requires --build")
    raise SystemExit(build(args.output_root.resolve() if args.output_root else ROOT) if args.build else check())
