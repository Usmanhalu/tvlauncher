#!/usr/bin/env python3
"""BraviaGlass v1.3.7 adaptive glass dialogs and launcher menus.

Apply after the version 1.3.6 patch. Reuse original signing configuration.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
src=root/"app/src/main/java/com/usman/braviaglass"
M=src/"MainActivity.java"
G=src/"GlassView.java"
B=root/"app/build.gradle"

def replace_once(file,old,new):
    data=file.read_text(encoding="utf-8")
    count=data.count(old)
    if count!=1:
        raise RuntimeError(f"{file.name}: expected exactly one match for {old[:100]!r}, got {count}")
    file.write_text(data.replace(old,new,1),encoding="utf-8")

GLASS_THEME=r'''package com.usman.braviaglass;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.ColorFilter;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PixelFormat;
import android.graphics.Rect;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.drawable.Drawable;

/**
 * Native Android 9-compatible frosted-glass modal background.
 * Snapshot stays in RAM only; no image files or permissions.
 * Samples the underlying launcher and creates a small two-pass blurred bitmap.
 */
final class GlassTheme {
    private GlassTheme(){}

    static Drawable popup(GlassView view) {
        int accent=0xff567eaa;
        try { if(view!=null)accent=view.colorHome.selectedColor(); }
        catch(RuntimeException ignored){}
        Bitmap blurred=null;
        try { if(view!=null)blurred=snapshot(view); }
        catch(RuntimeException | OutOfMemoryError ignored){}
        float density=view==null?1f:view.getResources().getDisplayMetrics().density;
        return new Frosted(blurred,accent,density);
    }

    private static Bitmap snapshot(GlassView view) {
        int sw=view.getWidth(),sh=view.getHeight();
        if(sw<=0||sh<=0)return null;
        int w=Math.min(288,Math.max(120,sw/7));
        int h=Math.max(70,Math.min(220,Math.round(w*(float)sh/sw)));
        Bitmap bitmap=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);
        Canvas canvas=new Canvas(bitmap);
        canvas.scale(w/(float)sw,h/(float)sh);
        view.draw(canvas);
        int[] pixels=new int[w*h];
        bitmap.getPixels(pixels,0,w,0,0,w,h);
        int[] temp=new int[w*h];
        // Two separable box-blur passes: broad frost without UI-thread GPU effects.
        for(int pass=0;pass<2;pass++){
            for(int y=0;y<h;y++)for(int x=0;x<w;x++){
                int ar=0,ag=0,ab=0,n=0;
                for(int k=-5;k<=5;k++){
                    int xx=Math.max(0,Math.min(w-1,x+k));
                    int value=pixels[y*w+xx];
                    ar+=Color.red(value);ag+=Color.green(value);ab+=Color.blue(value);n++;
                }
                temp[y*w+x]=Color.rgb(ar/n,ag/n,ab/n);
            }
            for(int y=0;y<h;y++)for(int x=0;x<w;x++){
                int ar=0,ag=0,ab=0,n=0;
                for(int k=-5;k<=5;k++){
                    int yy=Math.max(0,Math.min(h-1,y+k));
                    int value=temp[yy*w+x];
                    ar+=Color.red(value);ag+=Color.green(value);ab+=Color.blue(value);n++;
                }
                pixels[y*w+x]=Color.rgb(ar/n,ag/n,ab/n);
            }
        }
        bitmap.setPixels(pixels,0,w,0,0,w,h);
        return bitmap;
    }

    private static final class Frosted extends Drawable {
        private final Bitmap blur;
        private final int accent;
        private final float density;
        private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
        private int overallAlpha=255;

        Frosted(Bitmap bitmap,int selected,float scale){
            blur=bitmap;
            accent=selected;
            density=Math.max(.5f,scale);
        }

        @Override public void draw(Canvas canvas){
            Rect b=getBounds();
            if(b.isEmpty())return;
            float left=b.left,top=b.top,right=b.right,bottom=b.bottom;
            float radius=25*density;
            RectF area=new RectF(left,top,right,bottom);
            Path clip=new Path();
            clip.addRoundRect(area,radius,radius,Path.Direction.CW);
            int save=canvas.save();
            canvas.clipPath(clip);
            paint.setStyle(Paint.Style.FILL);
            paint.setShader(null);
            if(blur!=null&&!blur.isRecycled()){
                float ratio=(float)b.width()/Math.max(1,b.height());
                int srcW=blur.getWidth(),srcH=blur.getHeight();
                if((float)srcW/srcH>ratio)srcW=Math.max(1,Math.min(srcW,Math.round(srcH*ratio)));
                else srcH=Math.max(1,Math.min(srcH,Math.round(srcW/ratio)));
                int sx=(blur.getWidth()-srcW)/2,sy=(blur.getHeight()-srcH)/2;
                paint.setColor(Color.WHITE);
                paint.setAlpha(Math.min(255,Math.round(208*overallAlpha/255f)));
                canvas.drawBitmap(blur,new Rect(sx,sy,sx+srcW,sy+srcH),area,paint);
            }
            // Muted selected-app tint, intentionally never a saturated solid block.
            int r=Math.round(Color.red(accent)*.43f+16*.57f);
            int g=Math.round(Color.green(accent)*.43f+22*.57f);
            int bl=Math.round(Color.blue(accent)*.43f+33*.57f);
            int from=Color.argb(Math.round(186*overallAlpha/255f),r,g,bl);
            int to=Color.argb(Math.round(218*overallAlpha/255f),
                Math.round(r*.70f),Math.round(g*.75f),Math.round(bl*.83f));
            paint.setAlpha(255);
            paint.setShader(new LinearGradient(left,top,right,bottom,
                new int[]{from,to},null,Shader.TileMode.CLAMP));
            canvas.drawRect(area,paint);
            paint.setShader(new LinearGradient(left,top,left,top+(bottom-top)*.48f,
                new int[]{Color.argb(Math.round(43*overallAlpha/255f),255,255,255),Color.TRANSPARENT},
                null,Shader.TileMode.CLAMP));
            canvas.drawRect(area,paint);
            paint.setShader(null);
            canvas.restoreToCount(save);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(1.15f*density);
            paint.setColor(0x63ffffff);
            paint.setAlpha(Math.round(100*overallAlpha/255f));
            canvas.drawRoundRect(area,radius,radius,paint);
            paint.setStyle(Paint.Style.FILL);
            paint.setAlpha(255);
        }

        @Override public void setAlpha(int alpha){overallAlpha=Math.max(0,Math.min(255,alpha));invalidateSelf();}
        @Override public void setColorFilter(ColorFilter cf){paint.setColorFilter(cf);invalidateSelf();}
        @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
    }
}
'''

new=src/"GlassTheme.java"
if new.exists():
    raise RuntimeError("GlassTheme.java already exists: patch is not idempotent")
new.write_text(GLASS_THEME,encoding="utf-8")

replace_once(M,
    '    void wifi(){system(new Intent(Settings.ACTION_WIFI_SETTINGS),new Intent(Settings.ACTION_WIRELESS_SETTINGS));}',
    r'''    // BraviaGlass Wi-Fi summary is glass; Android's own Wi-Fi settings remain native.
    void wifi(){
        info("Wi-Fi",networkLabel()+"\nДля выбора сети откройте системные настройки Sony TV.",
            ()->system(new Intent(Settings.ACTION_WIFI_SETTINGS),new Intent(Settings.ACTION_WIRELESS_SETTINGS)));
    }''')

replace_once(M,
    '    void style(AlertDialog dialog){\n        dialog.show();Window window=dialog.getWindow();if(window!=null){\n            GradientDrawable bg=new GradientDrawable();bg.setColor(0xf51c3447);bg.setCornerRadius(24*getResources().getDisplayMetrics().density);bg.setStroke(1,0x554d738e);window.setBackgroundDrawable(bg);\n            int width=Math.min(Math.round(640*getResources().getDisplayMetrics().density),Math.round(getResources().getDisplayMetrics().widthPixels*0.86f));window.setLayout(width,WindowManager.LayoutParams.WRAP_CONTENT);\n            window.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);\n        }\n    }',
    '''    void style(AlertDialog dialog){
        // One shared adaptive, translucent frosted look for every launcher-owned popup.
        // Capture the home view before the modal darkens the screen.
        android.graphics.drawable.Drawable backdrop=GlassTheme.popup(glass);
        dialog.show();
        Window window=dialog.getWindow();
        if(window!=null){
            window.setBackgroundDrawable(backdrop);
            window.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
            window.setDimAmount(.17f);
            int width=Math.min(Math.round(640*getResources().getDisplayMetrics().density),
                Math.round(getResources().getDisplayMetrics().widthPixels*.86f));
            window.setLayout(width,WindowManager.LayoutParams.WRAP_CONTENT);
            window.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        }
    }''')

# The launcher-controlled control panel and its full settings page use the same muted accent.
# They are drawn with Canvas rather than Android AlertDialog.
needle='    void drawControl(Canvas c){'
replacement='''    int mutedGlassTint(int opacity){
        int accent=colorHome.selectedColor();
        int r=Math.round(Color.red(accent)*.38f+20*.62f);
        int g=Math.round(Color.green(accent)*.38f+29*.62f);
        int b=Math.round(Color.blue(accent)*.38f+42*.62f);
        return Color.argb(opacity,r,g,b);
    }
    void drawControl(Canvas c){'''
replace_once(G,needle,replacement)
replace_once(G,
    'RectF panel=new RectF(1266,138,1858,966);glass(c,panel,40,0xb428414e);',
    'RectF panel=new RectF(1266,138,1858,966);glass(c,panel,40,mutedGlassTint(192));')
replace_once(G,
    '        rect(c,0,0,W,H,0xf00b1d2c);',
    '''        // Let the wallpaper and selected-app colour shine softly through settings.
        rect(c,0,0,W,H,0x9d07111f);
        glass(c,new RectF(52,54,1868,1020),34,mutedGlassTint(184));''')
replace_once(G,
    'glass(canvas,new RectF((W-width)/2,744,(W+width)/2,812),24,0xe61b303e);',
    'glass(canvas,new RectF((W-width)/2,744,(W+width)/2,812),24,mutedGlassTint(206));')

replace_once(B,"versionCode 17","versionCode 18")
replace_once(B,"versionName '1.3.6'","versionName '1.3.7'")

assert 'new AlertDialog.Builder(this)' in M.read_text(encoding='utf-8')
assert 'void tvSettings()' in M.read_text(encoding='utf-8')
assert 'void inputs()' in M.read_text(encoding='utf-8')
assert 'void launchTvTimer()' in G.read_text(encoding='utf-8')
assert 'else if(ambient())openAddPicker();' in G.read_text(encoding='utf-8')
assert 'host.prayerSettings()' in G.read_text(encoding='utf-8')
print("BraviaGlass 1.3.7: shared Android-9 frosted glass dialogs, muted adaptive tint, glass Wi-Fi status and launcher settings/control. Sony external apps retain native UI.")
