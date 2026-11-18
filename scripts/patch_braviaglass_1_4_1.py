#!/usr/bin/env python3
"""BraviaGlass 1.4.1: recover app dock after sleeping pet and restore pet animation.

The Android Canvas stack must be balanced across all pets and poses, including
the sleeping pose reached at 23:00. Night sleep is based on inactivity, not
simply wall clock time, so users can observe movement while using the remote.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
src=root/"app/src/main/java/com/usman/braviaglass"
P=src/"PetCompanion.java"
C=src/"ColorHome.java"
B=root/"app/build.gradle"
def change(path,old,new):
    text=path.read_text(encoding="utf-8")
    count=text.count(old)
    if count!=1:raise RuntimeError(f"{path.name}: expected one match for {old[:100]!r}; got {count}")
    path.write_text(text.replace(old,new,1),encoding="utf-8")

change(P,
'''        boolean sleep=view.store.bool("petNightSleep",true)&&(hour>=23||hour<6);
        long beat=Math.max(1400,mood==0?2900:mood==1?2150:1550);
        int slot=(int)((now/beat)%9);
        int pose=sleep?5:new int[]{0,3,1,1,2,4,0,6,7}[slot];''',
'''        // Night-time sleep only after inactivity; playing with the remote wakes
        // the pet even at 23:00. Never freeze the only active character at night.
        boolean sleep=view.store.bool("petNightSleep",true)
            &&(hour>=23||hour<6)
            &&SystemClock.elapsedRealtime()-view.host.lastInteraction>90000;
        long beat=mood==0?1900:mood==1?1100:720;
        int slot=(int)((now/beat)%9);
        int pose=sleep?((now/2800)%8==0?6:5):
            new int[]{0,3,1,1,2,4,0,6,7}[slot];''')

change(P,
'''        float baseX=300f+(float)Math.sin(now/5300.0)*(mood==0?45:125);''',
'''        // Wander along the entire app shelf and turn around at either end.
        float phase=(now%24000L)/12000f;
        float progress=phase<=1f?phase:2f-phase;
        float baseX=mood==0?315f+(float)Math.sin(now/4200.0)*110f:
            160f+1550f*progress;''')

change(P,
'''        float x=Math.max(108,Math.min(1805,baseX));
        float y=762;
        if(pose==2)y-=28+12*(float)Math.abs(Math.sin(now/190.0));
        if(pose==1)x+=17*(float)Math.sin(now/210.0);''',
'''        float x=Math.max(108,Math.min(1805,baseX));
        float y=754;
        if(pose==2)y-=23+16*(float)Math.abs(Math.sin(now/190.0));
        if(pose==1){
            x+=9*(float)Math.sin(now/150.0);
            y-=4*(float)Math.abs(Math.sin(now/190.0));
        }
        if(sleep)y-=1.5f*(float)Math.sin(now/500.0); // gentle breathing''')

change(P,
'''        canvas.save();
        canvas.translate(x-size/2,y-size);
        canvas.scale(size/100f,size/100f);''',
'''        // Store the exact Canvas save count. A nested pose transformation must
        // never leak into ColorHome.dock(), which follows this renderer.
        int saveLevel=canvas.save();
        canvas.translate(x-size/2,y-size);
        canvas.scale(size/100f,size/100f);''')

change(P,
'''        canvas.restore();
        // Modest refresh rate on Android TV 9, nothing running in the background.''',
'''        canvas.restoreToCount(saveLevel);
        // Modest refresh rate on Android TV 9, nothing running in the background.''')

change(P,
'''        if(pose==5){c.save();c.translate(0,28);c.scale(1,.68f);}''',
'''        // Important: the parent draw(Canvas) already saved the Canvas.
        // An unmatched c.save() here used to shrink the subsequent app dock.
        if(pose==5){c.translate(0,28);c.scale(1,.68f);}''')

# Make walking and hopping obvious in vector 2D/3D-style companions as well.
change(P,
'''        float hop=pose==2?-12:0;
        c.translate(0,hop);''',
'''        float hop=pose==2?-14:pose==1?-3:0;
        c.translate(0,hop);
        if(pose==1)c.rotate(-5,50,66);''')

change(P,
'''        oval(c,22,78,22,17,dark,volume);
        oval(c,58,78,22,17,dark,volume);''',
'''        float step=pose==1?7*(float)Math.sin(SystemClock.uptimeMillis()/165.0):0;
        oval(c,22-step,78,22,17,dark,volume);
        oval(c,58+step,78,22,17,dark,volume);''')

# Draw pet after tiles so its paws remain visible on top of the shelf. This
# only affects HOME because PetCompanion.draw checks the screen.
change(C,
'''        if(v.showPrayer())drawPremiumPrayers(c);
        pet.draw(c);
        dock(c);''',
'''        if(v.showPrayer())drawPremiumPrayers(c);
        dock(c);
        pet.draw(c);''')

# Reset focus when opening settings? NOT needed: do not touch navigation.
# Continue to preserve all other widgets and previous settings.
change(B,"versionCode 22","versionCode 23")
change(B,"versionName '1.4.0'","versionName '1.4.1'")
s=P.read_text(encoding="utf-8")
assert 'canvas.restoreToCount(saveLevel)' in s
assert 'if(pose==5){c.save();' not in s
assert 'SystemClock.elapsedRealtime()-view.host.lastInteraction>90000' in s
assert C.read_text(encoding="utf-8").count('dock(c);\n        pet.draw(c);')==1
assert 'petSettings()' in (src/"MainActivity.java").read_text(encoding="utf-8")
print("BraviaGlass v1.4.1: Canvas stack balanced, shelf kept visible, pets roam and wake on interaction.")
