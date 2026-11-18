#!/usr/bin/env python3
"""BraviaGlass 1.3.8 Adaptive Sunset UI. Apply after 1.3.7."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
src=root/"app/src/main/java/com/usman/braviaglass"
C,M,A,B=(src/"ColorHome.java",src/"MainActivity.java",src/"AppEntry.java",root/"app/build.gradle")
def rep(path,old,new):
    s=path.read_text(encoding="utf-8")
    if s.count(old)!=1:raise RuntimeError(f"{path.name}: expected one occurrence of {old[:85]!r}, got {s.count(old)}")
    path.write_text(s.replace(old,new,1),encoding="utf-8")
rep(C,"import java.util.*;","import java.util.*;\nimport java.io.*;")
rep(C,"    private final IdentityHashMap<Bitmap,Integer> customPalette=new IdentityHashMap<>();",
'''    private final IdentityHashMap<Bitmap,Integer> customPalette=new IdentityHashMap<>();
    private final Bitmap sunsetPhoto; // decoded once; never reallocated per animation frame
''')
rep(C,"    ColorHome(GlassView view){v=view;}",
'''    ColorHome(GlassView view){
        v=view;
        Bitmap photo=null;
        try(InputStream stream=v.getContext().getAssets().open("sunset-lake.jpg")){
            BitmapFactory.Options options=new BitmapFactory.Options();
            options.inPreferredConfig=Bitmap.Config.RGB_565;
            photo=BitmapFactory.decodeStream(stream,null,options);
        }catch(IOException|OutOfMemoryError ignored){}
        sunsetPhoto=photo;
    }''')
rep(C,
'        float t=Math.max(0,Math.min(1,(at-colorStarted)/800f));t=t*t*(3-2*t);',
'''        float duration=Math.max(200,Math.min(1000,v.store.number("sunsetTransition",450)));
        float t=Math.max(0,Math.min(1,(at-colorStarted)/duration));t=t*t*(3-2*t);''')
rep(C,
'''        AppEntry app=list.get(Math.min(v.selected,list.size()-1));Bitmap custom=v.host.customIcon(app.id);
        if(custom==null||custom.isRecycled())return app.accent;''',
'''        AppEntry app=list.get(Math.min(v.selected,list.size()-1));
        int tint=v.store.number("tint."+app.id,-1);
        if(tint!=-1)return tint|0xff000000;
        Bitmap custom=v.host.customIcon(app.id);
        if(custom==null||custom.isRecycled())return app.accent;''')
s=C.read_text(encoding="utf-8")
a=s.index("    void background(Canvas c){");b=s.index("    void draw(Canvas c){")
if a>=b:raise RuntimeError("Invalid renderer anchors")
new_bg='''    void background(Canvas c){
        long now=SystemClock.uptimeMillis();int target=selectedColor();
        if(target!=targetColor){fromColor=currentColor(now);targetColor=target;colorStarted=now;}
        int accent=currentColor(now);
        int duration=Math.max(200,Math.min(1000,v.store.number("sunsetTransition",450)));
        float strength=Math.max(0f,Math.min(.50f,v.store.number("sunsetTint",25)/100f));
        if(!v.store.bool("ambientColors",true))strength=0;
        Paint p=v.paint;p.setStyle(Paint.Style.FILL);p.setShader(null);
        p.setColor(Color.WHITE);p.setAlpha(255);p.setColorFilter(null);
        // A custom wallpaper takes precedence if the user explicitly selected one.
        Bitmap picture=!v.store.text("wallpaper","").isEmpty()&&v.wallpaper!=null?v.wallpaper:sunsetPhoto;
        if(picture!=null&&!picture.isRecycled()&&v.store.bool("sunsetBackground",true)){
            float red=(Color.red(accent)-128)/128f;
            float green=(Color.green(accent)-128)/128f;
            float blue=(Color.blue(accent)-128)/128f;
            // GPU-friendly matrix: the same photo is never regenerated or swapped.
            p.setColorFilter(new ColorMatrixColorFilter(new float[]{
                1+red*strength*.83f,0,0,0,red*strength*27,
                0,1+green*strength*.83f,0,0,green*strength*27,
                0,0,1+blue*strength*.83f,0,blue*strength*27,
                0,0,0,1,0
            }));
            c.drawBitmap(picture,null,new RectF(0,0,1920,1080),p);
            p.setColorFilter(null);
            // Softly tint the sky and its reflection separately.
            int alpha=Math.round(strength*85);
            int horizon=Color.argb(alpha,Color.red(accent),Color.green(accent),Color.blue(accent));
            p.setShader(new LinearGradient(0,0,0,1080,
                new int[]{horizon,0x00000000,horizon,0x00000000},
                new float[]{0f,.39f,.72f,1f},Shader.TileMode.CLAMP));
            c.drawRect(0,0,1920,1080,p);p.setShader(null);
        }else{
            // Old ambient look remains available in Settings.
            c.drawColor(BASE);
            int a=Math.round(28*strength/.25f);
            p.setShader(new RadialGradient(960,620,1300,new int[]{
                Color.argb(Math.max(0,Math.min(90,a)),Color.red(accent),Color.green(accent),Color.blue(accent)),
                Color.TRANSPARENT},null,Shader.TileMode.CLAMP));
            c.drawRect(0,0,1920,1080,p);p.setShader(null);
        }
        // Preserve legibility of time, prayer text and application names.
        p.setColor(Color.WHITE);p.setAlpha(255);
        p.setShader(new LinearGradient(0,0,0,1080,
            new int[]{0x8c070e20,0x32040b18,0x07040815,0x9f050918},
            new float[]{0,.24f,.58f,1},Shader.TileMode.CLAMP));
        c.drawRect(0,0,1920,1080,p);
        p.setShader(null);p.setColorFilter(null);
        if(v.store.bool("animations",true)&&now-colorStarted<duration)v.postInvalidateOnAnimation();
    }
'''
C.write_text(s[:a]+new_bg+s[b:],encoding="utf-8")
rep(C,
'''        if(clock){
            v.text(c,greet,84,85,18,0xffadb8cb,v.medium);''',
'''        if(clock){
            v.round(c,new RectF(65,40,685,253),24,0x17344a78,0x14ffffff,1);
            v.text(c,greet,84,85,18,0xffd4ddeb,v.medium);''')
rep(A,"        this.accent = AppPalette.color(id,banner!=null?banner:icon);",
      "        this.accent = AppPalette.color(id,icon!=null?icon:banner);")
rep(M,
'''                r.add(toggle("Адаптивная подсветка приложений","ambientColors",true));''',
'''                r.add(toggle("Адаптивная подсветка приложений","ambientColors",true));
                r.add(toggle("Фон с горами и закатом","sunsetBackground",true));
                r.add(row("Сила цвета заката",store.number("sunsetTint",25)+"%",()->choice("Адаптация цвета заката",new String[]{"Без тонировки","Лёгкая — 15%","Как в макете — 25%","Заметная — 35%","Яркая — 45%"},i->{store.put("sunsetTint",new int[]{0,15,25,35,45}[i]);glass.refresh();})));
                r.add(row("Плавность смены цвета",store.number("sunsetTransition",450)+" мс",()->choice("Смена оттенка",new String[]{"Быстро — 250 мс","Как в макете — 450 мс","Плавно — 700 мс","Медленно — 1000 мс"},i->{store.put("sunsetTransition",new int[]{250,450,700,1000}[i]);glass.refresh();})));''')
rep(M,
'''\"Скрыть приложение\",\"Сведения о приложении\",app.system?\"Настройки системного приложения\":\"Удалить приложение\"};''',
'''\"Скрыть приложение\",\"Сведения о приложении\",app.system?\"Настройки системного приложения\":\"Удалить приложение\",\"Цвет заката для приложения\"};''')
rep(M,
'''                case 7:uninstall(app);break;
            }
        });''',
'''                case 7:uninstall(app);break;
                case 8:
                    choice("Цвет заката · "+store.label(app),new String[]{"Автоматически по значку","Красный","Бирюзовый","Зелёный","Синий","Фиолетовый","Розовый","Оранжевый"},i->{
                        int[] colors={-1,0xffdf414c,0xff12b8ba,0xff2db969,0xff379bf0,0xff9756d8,0xffdc70b5,0xfff8a248};
                        store.put("tint."+app.id,colors[i]);glass.refresh();
                    });break;
            }
        });''')
rep(M,
'''                r.add(toggle("Фон с горами и закатом","sunsetBackground",true));''',
'''                r.add(toggle("Фон с горами и закатом","sunsetBackground",true));
                r.add(row("Своя фотография для заката","Выбрать JPG или PNG · оттенок сохранится",()->{
                    store.put("look","ambient");pick(PICK_WALLPAPER);
                }));''')
rep(M,
'''if(request==PICK_WALLPAPER){store.put("wallpaper",saved);store.put("look","classic");loadWallpaper();}''',
'''if(request==PICK_WALLPAPER){store.put("wallpaper",saved);
                    if(!store.text("look","ambient").equals("ambient"))store.put("look","classic");
                    loadWallpaper();}''')
rep(B,"versionCode 18","versionCode 19")
rep(B,"versionName '1.3.7'","versionName '1.3.8'")
g=(src/"GlassView.java").read_text(encoding="utf-8")
assert "host.prayerSettings()" in g and "void launchTvTimer()" in g
assert "GlassTheme.popup(glass)" in M.read_text(encoding="utf-8")
assert "else if(ambient())openAddPicker();" in g
print("BraviaGlass v1.3.8: image-grade sunset, per-icon automatic hues, profile overrides; existing data preserved.")
