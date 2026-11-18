#!/usr/bin/env python3
"""BraviaGlass 1.3.9: cinematic Sunset Premium, per-app glow and glass reflections.

Apply after 1.3.8, retaining installed app data and the existing APK signer.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
src=root/'app/src/main/java/com/usman/braviaglass'
C=src/'ColorHome.java';B=root/'app/build.gradle'

def rep(path,old,new):
    s=path.read_text(encoding='utf-8')
    if s.count(old)!=1:raise RuntimeError(f'{path.name}: expected once {old[:100]!r}, found {s.count(old)}')
    path.write_text(s.replace(old,new,1),encoding='utf-8')

def region(path,start,end,replacement):
    s=path.read_text(encoding='utf-8')
    if s.count(start)!=1 or s.count(end)!=1:raise RuntimeError(f'{path}: anchors not unique')
    a=s.index(start);b=s.index(end,a+len(start))
    path.write_text(s[:a]+replacement+s[b:],encoding='utf-8')

rep(C,'open("sunset-lake.jpg")','open("sunset-premium.webp")')
region(C,'    void background(Canvas c){','    void draw(Canvas c){','''    void background(Canvas c){
        long now=SystemClock.uptimeMillis();int desired=selectedColor();
        if(desired!=targetColor){fromColor=currentColor(now);targetColor=desired;colorStarted=now;}
        int accent=currentColor(now);
        int duration=Math.max(200,Math.min(1000,v.store.number("sunsetTransition",450)));
        float strength=Math.max(0f,Math.min(.45f,v.store.number("sunsetTint",25)/100f));
        if(!v.store.bool("ambientColors",true))strength=0;
        Paint p=v.paint;p.setStyle(Paint.Style.FILL);p.setShader(null);p.setColorFilter(null);
        p.setAlpha(255);p.setColor(Color.WHITE);
        Bitmap custom=!v.store.text("wallpaper","").isEmpty()?v.wallpaper:null;
        Bitmap picture=custom!=null&&!custom.isRecycled()?custom:sunsetPhoto;
        if(picture!=null&&!picture.isRecycled()&&v.store.bool("sunsetBackground",true)){
            // Keep one mountain/lake photograph. Shift its lighting gently rather
            // than bleaching the whole image with full-frame bright colors.
            p.setColorFilter(new ColorMatrixColorFilter(new float[]{
                1+strength*(Color.red(accent)-128)/500f,0,0,0,0,
                0,1+strength*(Color.green(accent)-128)/500f,0,0,0,
                0,0,1+strength*(Color.blue(accent)-128)/500f,0,0,
                0,0,0,1,0
            }));
            c.drawBitmap(picture,null,new RectF(0,0,1920,1080),p);p.setColorFilter(null);
            int a=Math.round(122*strength);
            int hue=Color.argb(a,Color.red(accent),Color.green(accent),Color.blue(accent));
            p.setShader(new LinearGradient(0,0,0,1080,
                new int[]{hue,0x00000000,0x00000000,hue},
                new float[]{0,.36f,.58f,1},Shader.TileMode.CLAMP));
            c.drawRect(0,0,1920,1080,p);p.setShader(null);
        }else{
            c.drawColor(BASE);
            int hue=Color.argb(Math.round(32*strength),Color.red(accent),Color.green(accent),Color.blue(accent));
            p.setShader(new RadialGradient(900,690,1250,new int[]{hue,Color.TRANSPARENT},null,Shader.TileMode.CLAMP));
            c.drawRect(0,0,1920,1080,p);p.setShader(null);
        }
        // Dark glass-safe regions at top and dock; keep middle panorama vivid.
        p.setColor(Color.WHITE);p.setAlpha(255);
        p.setShader(new LinearGradient(0,0,0,1080,
            new int[]{0x88010a23,0x3a06122b,0x06000000,0x20030a1d,0x9d030b20},
            new float[]{0,.24f,.48f,.65f,1},Shader.TileMode.CLAMP));
        c.drawRect(0,0,1920,1080,p);p.setShader(null);p.setColorFilter(null);
        if(v.store.bool("animations",true)&&now-colorStarted<duration)v.postInvalidateOnAnimation();
    }
''')

rep(C,
'''        if(v.showPrayer())v.drawPrayers(c);''',
'''        if(v.showPrayer()){prayerGlass(c);v.drawPrayers(c);}''')

rep(C,
'''        v.text(c,"BRAVIAGLASS",1836,1030,17,0xff657288,v.regular,Paint.Align.RIGHT);''',
'''        v.text(c,"BRAVIAGLASS",1836,1030,17,0xffdce8fa,v.regular,Paint.Align.RIGHT);''')

rep(C,
'''        v.round(c,net,32,active?0x3ae7edff:0x12e7edff,active?0xffe8f4ff:0x16ffffff,active?2:1);''',
'''        v.round(c,net,32,active?0x415d8ec7:0x2b203f72,active?0xffe8f4ff:0x70bfe7ff,active?2:1);
        premiumEdge(c,net,32,0xff5aaaff,active);''')
rep(C,
'''        v.round(c,r,32,active?0x3ae7edff:0x12e7edff,active?0xffe8f4ff:0x16ffffff,active?2:1);''',
'''        v.round(c,r,32,active?0x416ba6df:0x30213d74,active?0xffe8f4ff:0x70bfe7ff,active?2:1);
        premiumEdge(c,r,32,currentColor(SystemClock.uptimeMillis()),active);''')

rep(C,
'''        v.text(c,(v.moving?"↔  ":"")+v.ellipsize(name,1600,58),84,750,58,GlassView.WHITE,v.regular);''',
'''        v.round(c,new RectF(56,786,1865,1050),30,0x1007102b,0x1dffffff,1);
        v.text(c,(v.moving?"↔  ":"")+v.ellipsize(name,1600,58),84,750,58,GlassView.WHITE,v.regular);''')
rep(C,
'''        c.save();c.clipRect(60,774,1860,1010);''',
'''        c.save();c.clipRect(60,774,1860,1065);''')
rep(C,
'''            v.softHalo(c,r,accent,selected);
            if(i<apps.size())tile(c,apps.get(i),r);''',
'''            premiumHalo(c,r,accent,selected);
            if(i<apps.size())tile(c,apps.get(i),r);''')
rep(C,
'''            if(v.screen==GlassView.Screen.HOME){RectF hit=new RectF(normal);hit.intersect(72,786,1848,1000);v.hits.add(new GlassView.Hit(hit,"dock",i));}''',
'''            premiumEdge(c,r,17,accent,selected);
            if(i<apps.size())premiumReflection(c,r,apps.get(i),selected);
            if(v.screen==GlassView.Screen.HOME){RectF hit=new RectF(normal);hit.intersect(72,786,1848,1000);v.hits.add(new GlassView.Hit(hit,"dock",i));}''')

rep(C,
'''        v.round(c,r,17,AppPalette.blend(BASE,app.accent,.23f),0x20ffffff,1);''',
'''        v.round(c,r,17,AppPalette.blend(BASE,app.accent,.35f),0x44ffffff,1);''')

insert='    void recents(Canvas c){'
helpers='''    /** Glossy glass edge around tiles and controls; hue follows any app icon. */
    void premiumEdge(Canvas c,RectF r,float radius,int accent,boolean selected){
        Paint p=v.paint;
        p.setShader(new LinearGradient(r.left,r.top,r.right,r.bottom,
            new int[]{0xb7e4f4ff,AppPalette.blend(0xff576bff,accent,.62f),
                selected?0xfff5d4ff:0x8f8bbaff,AppPalette.blend(0xff4079e8,accent,.58f)},
            new float[]{0,.36f,.62f,1},Shader.TileMode.CLAMP));
        p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(selected?3.4f:1.45f);p.setAlpha(255);
        c.drawRoundRect(r,radius,radius,p);p.setShader(null);p.setStyle(Paint.Style.FILL);
        if(selected){
            float cx=r.centerX();
            p.setShader(new RadialGradient(cx,r.top,Math.max(72,r.width()*.48f),
                new int[]{0xc8ffffff,0x49b8dfff,Color.TRANSPARENT},
                new float[]{0,.17f,1},Shader.TileMode.CLAMP));
            c.drawRect(r.left,r.top-10,r.right,r.top+15,p);p.setShader(null);
        }
        p.setAlpha(255);
    }
    /** Smooth colour halo with no polygon or harsh rectangular bounds. */
    void premiumHalo(Canvas c,RectF r,int accent,boolean selected){
        if(!selected)return;
        Paint p=v.paint;
        float glow=.76f+.24f*v.pulse();
        int a=Math.round(86*glow);
        float x=r.centerX(),y=r.centerY()+r.height()*.15f;
        float rad=r.width()*.95f;
        p.setShader(new RadialGradient(x,y,rad,
            new int[]{Color.argb(a,Color.red(accent),Color.green(accent),Color.blue(accent)),
                0x36374bff,Color.TRANSPARENT},new float[]{0,.32f,1},Shader.TileMode.CLAMP));
        p.setStyle(Paint.Style.FILL);p.setAlpha(255);
        c.drawRect(x-rad,y-rad,x+rad,y+rad,p);p.setShader(null);
        if(v.store.bool("animations",true))v.postInvalidateDelayed(50);
    }
    /** Actual upside-down mini-reflection of each tile on the virtual glass shelf. */
    void premiumReflection(Canvas c,RectF r,AppEntry app,boolean selected){
        float gap=7,scale=.35f;
        int a=c.saveLayerAlpha(r.left,r.bottom+gap,r.right,r.bottom+gap+r.height()*scale,selected?72:40);
        c.clipRect(r.left,r.bottom+gap,r.right,r.bottom+gap+r.height()*scale);
        c.translate(0,(1+scale)*r.bottom+gap);c.scale(1,-scale);
        tile(c,app,r);
        c.restoreToCount(a);
        Paint p=v.paint;p.setAlpha(255);p.setStyle(Paint.Style.FILL);
        p.setShader(new LinearGradient(0,r.bottom+gap,0,r.bottom+gap+r.height()*scale,
            new int[]{0x0004101c,0xc9000b20},null,Shader.TileMode.CLAMP));
        c.drawRect(r.left,r.bottom+gap,r.right,r.bottom+gap+r.height()*scale,p);
        p.setShader(null);
    }
    /** Glass capsule for all six prayers; active prayer gets a quiet cyan focus. */
    void prayerGlass(Canvas c){
        RectF panel=new RectF(482,244,1438,337);
        v.round(c,panel,23,0x4b071731,0x509dc9ff,1.1f);
        Paint p=v.paint;
        p.setShader(new LinearGradient(panel.left,panel.top,panel.right,panel.bottom,
            new int[]{0x28ffffff,0x00000000,0x18caadff},null,Shader.TileMode.CLAMP));
        c.drawRoundRect(panel,23,23,p);p.setShader(null);
        PrayerTimes.Display d=v.host.prayers.display(v.now());
        if(d!=null&&d.active>=0&&d.active<6){
            float width=924f/6f,cx=(1920-924)/2f+width*(d.active+.5f);
            RectF focus=new RectF(cx-72,247,cx+72,333);
            v.round(c,focus,18,0x494187b8,0x7b8decff,1.3f);
            p.setShader(new RadialGradient(cx,333,78,
                new int[]{0xa200e6ff,0x4500b5ff,Color.TRANSPARENT},
                new float[]{0,.24f,1},Shader.TileMode.CLAMP));
            c.drawRect(cx-78,320,cx+78,342,p);p.setShader(null);
        }
    }
'''
rep(C,insert,helpers+insert)
rep(B,'versionCode 19','versionCode 20')
rep(B,"versionName '1.3.8'","versionName '1.3.9'")
s=C.read_text(encoding='utf-8');assert 'sunset-premium.webp' in s
assert 'premiumHalo' in s and 'premiumReflection' in s and 'prayerGlass' in s
assert 'openAddPicker' in (src/'GlassView.java').read_text(encoding='utf-8')
print('BraviaGlass 1.3.9 Sunset Premium applied: glossy app tiles, mirrored reflections, gradient outlines, prayer glass and vibrant photo.')
