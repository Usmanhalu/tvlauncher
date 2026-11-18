#!/usr/bin/env python3
"""Generate a tiny shaded 3D-style panda atlas for Sony Android TV 9.
No rendering engine or network is needed at runtime."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import math,sys

SIZE=180
def ellipse(img,rect,fill,highlight=0):
    # Soft 3D-style elliptical shading with tiny catchlight.
    d=ImageDraw.Draw(img,"RGBA")
    d.ellipse(rect,fill=fill)
    if highlight:
        x0,y0,x1,y1=rect
        ww=(x1-x0);hh=(y1-y0)
        top=(x0+ww*.15,y0+hh*.08,x0+ww*.67,y0+hh*.45)
        glow=Image.new("RGBA",img.size,(0,0,0,0))
        ImageDraw.Draw(glow).ellipse(top,fill=(255,255,255,highlight))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(max(1,int(ww*.09)))))
def frame(pose):
    s=3
    canvas=Image.new("RGBA",(SIZE*s,SIZE*s),(0,0,0,0))
    def e(rect,color,hi=0):
        ellipse(canvas,tuple(int(t*s) for t in rect),color,hi)
    def line(points,color,width):
        d=ImageDraw.Draw(canvas,"RGBA")
        d.line([(int(x*s),int(y*s)) for x,y in points],fill=color,width=int(width*s),joint="curve")
    sleepy=pose==5; leap=pose==2; wave=pose in (3,4); yawn=pose==6; peek=pose==7
    xshift=13 if pose==1 else 0
    cy=17 if leap else 29
    # Soft ground shadow
    if not leap:
        e((42,156,146,170),(3,8,24,40))
    # ears
    e((37+xshift,cy+1,80+xshift,cy+49),(26,26,32,255),55)
    e((116+xshift,cy+1,159+xshift,cy+49),(26,26,32,255),55)
    if peek:
        cy=64
    # body and belly
    e((44+xshift,cy+79,154+xshift,cy+149),(18,22,30,255),43)
    e((64+xshift,cy+86,135+xshift,cy+146),(241,241,237,255),100)
    # left arm
    e((27+xshift,cy+89,70+xshift,cy+137),(29,32,39,255),45)
    if wave:
        e((142+xshift,cy+52,171+xshift,cy+108),(31,35,43,255),65)
        e((147+xshift,cy+47,168+xshift,cy+73),(25,29,38,255),50)
    else:
        e((125+xshift,cy+91,161+xshift,cy+140),(26,31,39,255),45)
    # feet, sleeping pose flattened by later affine transform
    e((40+xshift,cy+128,84+xshift,cy+158),(24,28,35,255),60)
    e((115+xshift,cy+128,160+xshift,cy+158),(25,29,36,255),60)
    for cx in (65+xshift,137+xshift):
        e((cx-7,cy+138,cx+7,cy+153),(235,133,145,255),35)
    # big baby panda face
    e((30+xshift,cy+23,164+xshift,cy+128),(248,247,243,255),100)
    # 3D shadow cheeks
    e((45+xshift,cy+78,77+xshift,cy+113),(236,231,229,80))
    e((116+xshift,cy+78,149+xshift,cy+113),(232,223,224,80))
    # dark eye patches
    e((54+xshift,cy+53,92+xshift,cy+96),(35,39,46,255),15)
    e((105+xshift,cy+53,143+xshift,cy+96),(35,39,46,255),15)
    if sleepy:
        line([(62+xshift,cy+76),(77+xshift,cy+79),(88+xshift,cy+75)],(245,239,242,255),2.4)
        line([(109+xshift,cy+75),(123+xshift,cy+79),(135+xshift,cy+75)],(245,239,242,255),2.4)
    else:
        e((65+xshift,cy+64,84+xshift,cy+90),(253,248,251,255),100)
        e((111+xshift,cy+64,132+xshift,cy+90),(252,249,250,255),100)
        e((71+xshift,cy+69,83+xshift,cy+84),(37,55,75,255),120)
        e((115+xshift,cy+69,127+xshift,cy+84),(37,55,75,255),120)
        e((72+xshift,cy+70,76+xshift,cy+75),(255,255,255,255))
        e((116+xshift,cy+70,120+xshift,cy+75),(255,255,255,255))
    e((89+xshift,cy+94,108+xshift,cy+108),(39,38,43,255),70)
    if yawn:
        e((88+xshift,cy+107,111+xshift,cy+133),(67,26,30,255),45)
        e((93+xshift,cy+125,106+xshift,cy+130),(239,139,147,255))
    else:
        line([(90+xshift,cy+113),(97+xshift,cy+117),(105+xshift,cy+113)],(66,52,58,255),2.1)
    # blush and pink pads
    e((49+xshift,cy+94,70+xshift,cy+105),(241,144,156,47))
    e((129+xshift,cy+94,149+xshift,cy+105),(241,144,156,47))
    if pose==4:
        e((149,19,166,31),(255,190,41,255),20)
        e((163,19,177,31),(255,122,27,255),25)
    if sleepy:
        small=canvas.rotate(-11,Image.Resampling.BICUBIC,expand=False)
        canvas=small.transform(canvas.size,Image.Transform.AFFINE,(1,0,0,0,.73,SIZE*s*.18),resample=Image.Resampling.BICUBIC)
    if peek:
        canvas=canvas.transform(canvas.size,Image.Transform.AFFINE,(1,0,0,0,1,-30*s),resample=Image.Resampling.BICUBIC)
    canvas.thumbnail((128,128),Image.Resampling.LANCZOS)
    target=Image.new("RGBA",(128,128),(0,0,0,0))
    target.alpha_composite(canvas,((128-canvas.width)//2,(128-canvas.height)//2))
    return target

def main():
    assets=Path(sys.argv[1])/"app/src/main/assets"
    assets.mkdir(parents=True,exist_ok=True)
    atlas=Image.new("RGBA",(512,256),(0,0,0,0))
    for i in range(8):
        atlas.alpha_composite(frame(i),(i%4*128,i//4*128))
    dest=assets/"pet-panda-3d.webp"
    atlas.save(dest,format="WEBP",quality=76,method=6)
    assert dest.stat().st_size>2000
    print("Bundled 8-frame shaded panda atlas",dest.stat().st_size)
if __name__=="__main__":main()
