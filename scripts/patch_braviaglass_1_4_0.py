#!/usr/bin/env python3
"""BraviaGlass v1.4.0: five time-of-day scenes and small optional animated pets."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
src=root/"app/src/main/java/com/usman/braviaglass"
C=src/"ColorHome.java"
M=src/"MainActivity.java"
B=root/"app/build.gradle"

def change(path,old,new):
    s=path.read_text(encoding="utf-8")
    n=s.count(old)
    if n!=1:raise RuntimeError(f"{path.name}: expected once {old[:90]!r}; found {n}")
    path.write_text(s.replace(old,new,1),encoding="utf-8")

PET=r'''package com.usman.braviaglass;

import android.graphics.*;
import android.os.SystemClock;
import java.io.InputStream;
import java.io.IOException;
import java.util.Calendar;

/**
 * Lightweight pet: 3D-looking premade panda frames + vector 2D/3D-style
 * alternate characters. Drawn into the launcher, never as a floating window.
 * No sound by default; never steals remote input or app focus.
 */
final class PetCompanion {
    private final GlassView view;
    private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
    private final Bitmap pandaFrames;
    private long lastSelectionAt=0;
    private int lastSelection=-1;

    PetCompanion(GlassView view){
        this.view=view;
        Bitmap image=null;
        try(InputStream stream=view.getContext().getAssets().open("pet-panda-3d.webp")){
            image=BitmapFactory.decodeStream(stream);
        }catch(IOException | OutOfMemoryError ignored){}
        pandaFrames=image;
    }

    void draw(Canvas canvas){
        if(!view.store.bool("petEnabled",true)||!view.ambient()
            ||view.screen!=GlassView.Screen.HOME)return;
        long now=SystemClock.uptimeMillis();
        int active=view.selected;
        if(active!=lastSelection){lastSelection=active;lastSelectionAt=now;}
        String kind=view.store.text("petKind","panda");
        String style=view.store.text("petStyle","3d");
        int mood=view.store.number("petActivity",2);
        int percent=Math.max(30,Math.min(60,view.store.number("petSize",40)));
        float size=90f*percent/40f; // 40% setting: about 8.3% of 1080p height
        int hour=Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        boolean sleep=view.store.bool("petNightSleep",true)&&(hour>=23||hour<6);
        long beat=Math.max(1400,mood==0?2900:mood==1?2150:1550);
        int slot=(int)((now/beat)%9);
        int pose=sleep?5:new int[]{0,3,1,1,2,4,0,6,7}[slot];
        if(!view.store.bool("petRun",true)&&(pose==1||pose==2))pose=0;
        if(!view.store.bool("petPlay",true)&&pose==4)pose=0;
        float baseX=300f+(float)Math.sin(now/5300.0)*(mood==0?45:125);
        float tile=view.store.number("dockSize",100)>=115?320:280;
        float target=84+view.selected*(tile+26)-view.colorHome.rowOffset(now)+tile*.5f;
        if(now-lastSelectionAt<3000&&active<view.dockApps().size()){
            baseX=baseX*.28f+Math.max(130,Math.min(1750,target))*.72f;
        }
        float x=Math.max(108,Math.min(1805,baseX));
        float y=762;
        if(pose==2)y-=28+12*(float)Math.abs(Math.sin(now/190.0));
        if(pose==1)x+=17*(float)Math.sin(now/210.0);
        if(view.store.bool("petClimb",true)&&!sleep&&slot==8&&mood==2){
            x=1015;y=615; // rare playful visit to the bottom edge of the clock
        }
        canvas.save();
        canvas.translate(x-size/2,y-size);
        canvas.scale(size/100f,size/100f);
        if("panda".equals(kind)&&"3d".equals(style)&&pandaFrames!=null&&!pandaFrames.isRecycled()){
            int cellW=pandaFrames.getWidth()/4,cellH=pandaFrames.getHeight()/2;
            Rect source=new Rect(pose%4*cellW,pose/4*cellH,
                (pose%4+1)*cellW,(pose/4+1)*cellH);
            p.setAlpha(255);p.setShader(null);p.setStyle(Paint.Style.FILL);
            canvas.drawBitmap(pandaFrames,source,new RectF(0,0,100,100),p);
        }else{
            drawCharacter(canvas,kind,style,pose);
        }
        canvas.restore();
        // Modest refresh rate on Android TV 9, nothing running in the background.
        if(view.store.bool("animations",true))
            view.postInvalidateDelayed(view.store.bool("petPowerSave",true)?125:75);
    }

    private void oval(Canvas c,float x,float y,float w,float h,int color,boolean volume){
        p.setStyle(Paint.Style.FILL);
        if(volume){
            p.setShader(new RadialGradient(x+w*.35f,y+h*.20f,
                Math.max(w,h)*.83f,
                new int[]{AppPalette.blend(color,Color.WHITE,.38f),color,
                    AppPalette.blend(color,Color.BLACK,.35f)},
                new float[]{0,.56f,1},Shader.TileMode.CLAMP));
        }else{
            p.setShader(null);p.setColor(color);
        }
        c.drawOval(new RectF(x,y,x+w,y+h),p);
        p.setShader(null);
    }
    private void drawCharacter(Canvas c,String kind,String style,int pose){
        boolean volume="3d".equals(style);
        int fur=0xfff6f3ea,dark=0xff2a303e,belly=0xfffaf8f2;
        if("cat".equals(kind)){fur=0xffbcb5b7;dark=0xff646875;belly=0xfff7f5f0;}
        if("dog".equals(kind)){fur=0xffdca86e;dark=0xff805338;belly=0xfff5d9ab;}
        if("fox".equals(kind)){fur=0xffff924b;dark=0xff8e392f;belly=0xffffe8c9;}
        if("robot".equals(kind)){fur=0xffdcefff;dark=0xff285194;belly=0xff79d9ff;}
        if("dragon".equals(kind)){fur=0xffaa83e3;dark=0xff5f4095;belly=0xffeccbff;}
        if("spirit".equals(kind)){fur=0xff62dcfc;dark=0xff3789d9;belly=0xffeeffff;}
        // Tiny elliptical ground shadow and paws.
        oval(c,13,92,75,6,0x65050b24,false);
        if(pose==5){c.save();c.translate(0,28);c.scale(1,.68f);}
        float hop=pose==2?-12:0;
        c.translate(0,hop);
        oval(c,22,51,55,45,kind.equals("panda")?dark:fur,volume);
        oval(c,31,56,38,34,belly,volume);
        if("robot".equals(kind)){
            p.setColor(dark);p.setShader(null);
            c.drawRoundRect(new RectF(21,15,79,63),15,15,p);
            p.setColor(fur);c.drawRoundRect(new RectF(26,19,74,58),12,12,p);
            p.setColor(0xff11294b);c.drawRoundRect(new RectF(30,29,70,50),10,10,p);
            p.setColor(0xff19ecff);c.drawOval(new RectF(36,35,43,43),p);
            c.drawOval(new RectF(57,35,64,43),p);
            oval(c,13,66,16,21,dark,volume);oval(c,72,66,15,21,dark,volume);
            return;
        }
        if("spirit".equals(kind)){
            oval(c,23,12,54,77,fur,volume);
            oval(c,35,42,9,12,dark,false);oval(c,57,42,9,12,dark,false);
            return;
        }
        if("fox".equals(kind)||"cat".equals(kind)||"dragon".equals(kind)){
            // Pointed ears, subtly different tail colours.
            Path ears=new Path();
            ears.moveTo(21,30);ears.lineTo(19,4);ears.lineTo(44,17);
            ears.lineTo(56,17);ears.lineTo(81,4);ears.lineTo(79,30);ears.close();
            p.setStyle(Paint.Style.FILL);p.setColor(fur);c.drawPath(ears,p);
            oval(c,70,54,25,22,dark,volume);
        }else{
            oval(c,18,9,25,28,dark,volume);
            oval(c,57,9,25,28,dark,volume);
        }
        if("dog".equals(kind)){
            oval(c,15,14,21,46,dark,volume);
            oval(c,65,14,21,46,dark,volume);
        }
        oval(c,19,18,63,59,fur,volume);
        if("panda".equals(kind)){
            oval(c,24,36,22,23,dark,volume);
            oval(c,55,36,22,23,dark,volume);
        }
        oval(c,34,43,9,11,belly,false);
        oval(c,58,43,9,11,belly,false);
        oval(c,37,46,5,7,0xff1b2031,false);
        oval(c,60,46,5,7,0xff1b2031,false);
        oval(c,46,58,10,7,dark,volume);
        if(pose==3||pose==4){
            oval(c,2,49,18,23,dark,volume);
        }
        oval(c,22,78,22,17,dark,volume);
        oval(c,58,78,22,17,dark,volume);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(2.2f);p.setColor(dark);
        c.drawArc(new RectF(43,64,59,74),0,180,false,p);
        p.setStyle(Paint.Style.FILL);
        if(pose==4){
            p.setColor(0xffffd84c);c.drawCircle(95,23,5,p);
            p.setColor(0xffe377ff);c.drawOval(new RectF(83,11,95,22),p);
        }
    }
}
'''
(src/"PetCompanion.java").write_text(PET,encoding="utf-8")

change(C,
'''    private final Bitmap sunsetPhoto; // decoded once; never reallocated per animation frame''',
'''    private final Bitmap sunsetPhoto; // decoded once; never reallocated per animation frame
    private final Bitmap[] dayScenes=new Bitmap[5];
    private final PetCompanion pet;
    private int displayedDayScene=-1,previousDayScene=-1;
    private long sceneStarted=0;
    private static final String[] DAY_IDS={"morning","noon","sunset","evening","night"};''')
change(C,
'''        sunsetPhoto=photo;
    }''',
'''        sunsetPhoto=photo;
        for(int i=0;i<DAY_IDS.length;i++){
            try(InputStream stream=v.getContext().getAssets().open("dynamic-scenes/"+DAY_IDS[i]+".webp")){
                BitmapFactory.Options o=new BitmapFactory.Options();
                o.inPreferredConfig=Bitmap.Config.RGB_565;
                dayScenes[i]=BitmapFactory.decodeStream(stream,null,o);
            }catch(IOException|OutOfMemoryError ignored){}
        }
        pet=new PetCompanion(v);
    }
    int daySceneIndex(){
        if(v.store.text("daySceneMode","auto").equals("manual")){
            return Math.max(0,Math.min(4,v.store.number("daySceneFixed",2)));
        }
        Calendar now=Calendar.getInstance();
        now.setTimeInMillis(v.now());
        int h=now.get(Calendar.HOUR_OF_DAY);
        return h>=6&&h<11?0:h>=11&&h<16?1:h>=16&&h<19?2:h>=19&&h<23?3:4;
    }''')

# Adapt scenic image selection while preserving user-selected image priority.
change(C,
'''        Bitmap picture=custom!=null&&!custom.isRecycled()?custom:sunsetPhoto;
        if(picture!=null&&!picture.isRecycled()&&v.store.bool("sunsetBackground",true)){''',
'''        int scene=daySceneIndex();
        Bitmap chosen=dayScenes[scene]!=null?dayScenes[scene]:sunsetPhoto;
        Bitmap picture=custom!=null&&!custom.isRecycled()?custom:chosen;
        if(displayedDayScene<0)displayedDayScene=scene;
        if(scene!=displayedDayScene){
            previousDayScene=displayedDayScene;
            displayedDayScene=scene;
            sceneStarted=now;
        }
        float sceneFade=Math.max(0,Math.min(1,(now-sceneStarted)/1100f));
        if(picture!=null&&!picture.isRecycled()&&v.store.bool("sunsetBackground",true)){''')
change(C,
'''            c.drawBitmap(picture,null,new RectF(0,0,1920,1080),p);p.setColorFilter(null);''',
'''            if(custom==null&&previousDayScene>=0&&sceneFade<1
                &&dayScenes[previousDayScene]!=null){
                p.setAlpha(Math.round(255*(1-sceneFade)));
                c.drawBitmap(dayScenes[previousDayScene],null,new RectF(0,0,1920,1080),p);
                p.setAlpha(Math.round(255*sceneFade));
                c.drawBitmap(picture,null,new RectF(0,0,1920,1080),p);
            }else{
                p.setAlpha(255);
                c.drawBitmap(picture,null,new RectF(0,0,1920,1080),p);
            }
            p.setAlpha(255);p.setColorFilter(null);''')
change(C,
'''        if(v.store.bool("animations",true)&&now-colorStarted<duration)v.postInvalidateOnAnimation();''',
'''        if(v.store.bool("animations",true)&&
           (now-colorStarted<duration||now-sceneStarted<1100))
            v.postInvalidateOnAnimation();''')
change(C,
'''        if(v.showPrayer())drawPremiumPrayers(c);
        dock(c);''',
'''        if(v.showPrayer())drawPremiumPrayers(c);
        pet.draw(c);
        dock(c);''')

# Keep full application tiles visible; scroll in whole-tile increments, not half tiles.
change(C,
'''        float desired=Math.max(0,Math.min(v.selected*(size+gap)+size/2-available/2,Math.max(0,total-available)));''',
'''        int visible=Math.max(1,(int)Math.floor((available+gap)/(size+gap)));
        int first=Math.max(0,Math.min(v.selected-visible/2,Math.max(0,dockCount-visible)));
        float desired=first*(size+gap);''')
# The pet should only appear on the Home screen; never cover dialogs or controls.

change(M,
'''                r.add(toggle("Фон с горами и закатом","sunsetBackground",true));''',
'''                r.add(toggle("Фон с горами и закатом","sunsetBackground",true));
                r.add(row("Пять сцен времени суток",
                    store.text("daySceneMode","auto").equals("auto")?"Автоматически":"Выбрана вручную",
                    this::chooseDaySceneMode));
                r.add(row("Питомец на главном экране",
                    (store.bool("petEnabled",true)?"Включён":"Выключен")+
                    " · "+petLabel(store.text("petKind","panda"))+" · "+
                    store.text("petStyle","3d").toUpperCase(java.util.Locale.ROOT),
                    this::petSettings));''')

change(M,'''    List<SettingRow> rows(int category){''',
'''    static String petLabel(String kind){
        switch(kind){
            case "cat":return "Котик";
            case "dog":return "Щенок";
            case "fox":return "Лисёнок";
            case "panda":return "Панда";
            case "robot":return "Мини-робот";
            case "dragon":return "Дракончик";
            case "spirit":return "Светящийся дух";
            default:return "Панда";
        }
    }
    void chooseDaySceneMode(){
        choice("Пять динамических фонов",
            new String[]{"Автоматическая смена (по времени ТВ)",
                "Выбрать сцену вручную"},i->{
            if(i==0){store.put("daySceneMode","auto");glass.refresh();}
            else choice("Ручной выбор сцены",
                new String[]{"Утро","День","Закат","Вечер","Ночь"},index->{
                    store.put("daySceneMode","manual");
                    store.put("daySceneFixed",index);
                    glass.refresh();
                });
        });
    }
    void petSettings(){
        String[] names={
            store.bool("petEnabled",true)?"Показать питомца: ВКЛ":"Показать питомца: ВЫКЛ",
            "Выбрать персонажа: "+petLabel(store.text("petKind","panda")),
            "Стиль: "+store.text("petStyle","3d").toUpperCase(java.util.Locale.ROOT),
            "Размер: "+store.number("petSize",40)+"% от демонстрации",
            "Характер: "+new String[]{"Спокойный","Обычный","Игривый"}[Math.max(0,Math.min(2,store.number("petActivity",2)))],
            "Бегать по приложениям: "+(store.bool("petRun",true)?"ВКЛ":"ВЫКЛ"),
            "Играть с предметами: "+(store.bool("petPlay",true)?"ВКЛ":"ВЫКЛ"),
            "Залезать на часы: "+(store.bool("petClimb",true)?"ВКЛ":"ВЫКЛ"),
            "Ночной сон: "+(store.bool("petNightSleep",true)?"ВКЛ":"ВЫКЛ"),
            "Звуки питомца: "+(store.bool("petSounds",false)?"ВКЛ":"ВЫКЛ"),
            "Энергосбережение: "+(store.bool("petPowerSave",true)?"ВКЛ":"ВЫКЛ")
        };
        choice("Питомец · BraviaGlass",names,i->{
            if(i==0||i>=5){
                String[] keys={"petEnabled","petRun","petPlay","petClimb","petNightSleep","petSounds","petPowerSave"};
                int idx=i==0?0:i-4;
                store.put(keys[idx],!store.bool(keys[idx],idx!=5));
                glass.refresh();petSettings();return;
            }
            switch(i){
                case 1:choice("Выберите персонажа",
                    new String[]{"Панда","Котик","Щенок","Лисёнок","Мини-робот","Дракончик","Светящийся дух"},k->{
                        String[] values={"panda","cat","dog","fox","robot","dragon","spirit"};
                        store.put("petKind",values[k]);
                        if(k==5)store.put("petStyle","3d");
                        if(k==6)store.put("petStyle","2d");
                        glass.refresh();petSettings();
                    });break;
                case 2:choice("Оформление питомца",
                    new String[]{"2D — лёгкий мультяшный","3D — объёмный (готовые кадры)"},k->{
                        store.put("petStyle",k==0?"2d":"3d");
                        String kind=store.text("petKind","panda");
                        if(k==0&&kind.equals("dragon"))store.put("petKind","panda");
                        if(k==1&&kind.equals("spirit"))store.put("petKind","panda");
                        glass.refresh();petSettings();
                    });break;
                case 3:choice("Размер питомца",
                    new String[]{"30%","35%","40%","45%","50%","55%","60%"},k->{
                        store.put("petSize",new int[]{30,35,40,45,50,55,60}[k]);
                        glass.refresh();petSettings();
                    });break;
                case 4:choice("Характер питомца",
                    new String[]{"Спокойный","Обычный","Игривый"},k->{
                        store.put("petActivity",k);
                        glass.refresh();petSettings();
                    });break;
            }
        });
    }
    List<SettingRow> rows(int category){''')

change(B,"versionCode 21","versionCode 22")
change(B,"versionName '1.3.10'","versionName '1.4.0'")
s=C.read_text(encoding="utf-8")
assert 'pet.draw(c)' in s and 'daySceneIndex()' in s
assert 'int visible=Math.max(1' in s
assert 'drawPremiumPrayers(c)' in s
assert 'topButton(c,new RectF(1790,82,1853,145)' in s
assert 'GlassTheme.popup(glass)' in M.read_text(encoding="utf-8")
assert 'void launchTvTimer()' in (src/"GlassView.java").read_text(encoding="utf-8")
print("BraviaGlass 1.4.0 pet and 5 daily scenes patch applied.")
