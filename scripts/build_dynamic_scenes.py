#!/usr/bin/env python3
"""Create five compact, consistent time-of-day lake scenes from the licensed
bundle image in the BraviaGlass package. Never uses external image sources."""
import argparse
import math
import random
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter

def composite_glow(image,xy,radius,color,opacity):
    glow=Image.new("RGBA",image.size,(0,0,0,0))
    draw=ImageDraw.Draw(glow)
    x,y=xy
    draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(*color,opacity))
    glow=glow.filter(ImageFilter.GaussianBlur(max(10,int(radius*.48))))
    return Image.alpha_composite(image,glow)

def scene(base,key):
    w,h=base.size
    r=ImageEnhance
    if key=="morning":
        p=r.Brightness(base).enhance(1.41)
        p=r.Contrast(p).enhance(1.04)
        p=r.Color(p).enhance(.86)
        p=Image.blend(p,Image.new("RGB",base.size,(255,205,150)),.10)
    elif key=="noon":
        p=r.Brightness(base).enhance(1.70)
        p=r.Contrast(p).enhance(1.08)
        p=r.Color(p).enhance(.78)
        p=Image.blend(p,Image.new("RGB",base.size,(89,183,255)),.19)
    elif key=="sunset":
        p=r.Color(base).enhance(1.20)
        p=r.Contrast(p).enhance(1.05)
    elif key=="evening":
        p=r.Brightness(base).enhance(.72)
        p=r.Color(p).enhance(1.13)
        p=Image.blend(p,Image.new("RGB",base.size,(53,42,116)),.17)
    else:
        p=r.Brightness(base).enhance(.35)
        p=r.Color(p).enhance(.58)
        p=Image.blend(p,Image.new("RGB",base.size,(3,21,65)),.33)
    p=p.convert("RGBA")
    if key=="morning":
        p=composite_glow(p,(int(w*.81),int(h*.44)),int(w*.20),(255,213,135),52)
    if key=="noon":
        p=composite_glow(p,(int(w*.78),int(h*.28)),int(w*.18),(239,249,255),59)
    if key=="sunset":
        p=composite_glow(p,(int(w*.83),int(h*.53)),int(w*.19),(255,143,45),55)
    if key=="evening":
        p=composite_glow(p,(int(w*.81),int(h*.46)),int(w*.13),(172,87,241),37)
    if key=="night":
        stars=Image.new("RGBA",base.size,(0,0,0,0))
        d=ImageDraw.Draw(stars)
        rng=random.Random(2040)
        for _ in range(78):
            x=rng.randrange(10,w-10);y=rng.randrange(8,int(h*.39))
            r0=rng.choice([1,1,1,2]);a=rng.choice([110,165,210])
            d.ellipse((x-r0,y-r0,x+r0,y+r0),fill=(232,241,255,a))
        cx,cy=int(w*.83),int(h*.19);moonR=int(h*.029)
        d.ellipse((cx-moonR,cy-moonR,cx+moonR,cy+moonR),fill=(243,247,255,235))
        d.ellipse((cx-moonR//3,cy-moonR-int(moonR*.28),cx+moonR+int(moonR*.32),cy+moonR//2),fill=(16,37,89,240))
        p=Image.alpha_composite(p,stars)
        p=composite_glow(p,(cx,cy),int(w*.073),(119,162,255),31)
    return p.convert("RGB")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("project")
    args=parser.parse_args()
    assets=Path(args.project)/"app/src/main/assets"
    original=assets/"sunset-premium.webp"
    if not original.exists():raise SystemExit("Bundled sunset-premium.webp is required")
    base=Image.open(original).convert("RGB").resize((1280,720),Image.Resampling.LANCZOS)
    dest=assets/"dynamic-scenes";dest.mkdir(parents=True,exist_ok=True)
    for key in ("morning","noon","sunset","evening","night"):
        out=dest/(key+".webp")
        scene(base,key).save(out,format="WEBP",quality=76,method=6)
        assert out.stat().st_size>5000
        print(key,out.stat().st_size)
    (dest/"CREDITS.txt").write_text(
        "Five colour-graded scenes derived from the BraviaGlass v1.3.9 AI-generated Sunset Premium image. No remote downloads.\n",
        encoding="utf-8")
if __name__=="__main__":main()
