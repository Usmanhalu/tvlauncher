#!/usr/bin/env python3
"""BraviaGlass 1.3.10: user-approved second Sunset Premium layout.
Apply after 1.3.9; no change to package ID, signing, data or Android permissions.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
src=root/"app/src/main/java/com/usman/braviaglass"
C=src/"ColorHome.java"
G=src/"GlassView.java"
B=root/"app/build.gradle"

def once(path,old,new):
    data=path.read_text(encoding="utf-8")
    n=data.count(old)
    if n!=1:
        raise RuntimeError(f"{path.name}: expected one occurrence of {old[:110]!r}, found {n}")
    path.write_text(data.replace(old,new,1),encoding="utf-8")

def between(path,start,end,new):
    data=path.read_text(encoding="utf-8")
    if data.count(start)!=1 or data.count(end)!=1:
        raise RuntimeError(f"{path.name}: anchors are not unique")
    a=data.index(start);b=data.index(end,a+len(start))
    path.write_text(data[:a]+new+data[b:],encoding="utf-8")

between(C,"    void header(Canvas c){","    void topButton(Canvas c",'''    /** Center clock/date as in the approved second mockup; keep every top shortcut. */
    void header(Canvas c){
        Date date=new Date(v.now());
        boolean showClock=v.store.bool("showClock",true);
        String weekday=new SimpleDateFormat("EEEE",new Locale("ru")).format(date);
        if(!weekday.isEmpty())weekday=weekday.substring(0,1).toUpperCase(new Locale("ru"))+weekday.substring(1);
        String when=weekday+" "+new SimpleDateFormat("d MMMM",new Locale("ru")).format(date);
        if(showClock){
            v.text(c,when,960,276,38,0xfff4f7ff,v.medium,Paint.Align.CENTER);
        }else{
            v.text(c,when,960,337,36,0xfff4f7ff,v.medium,Paint.Align.CENTER);
        }
        if(v.store.bool("showWeather",true)){
            String weatherLine;
            if(v.weather==null)weatherLine=v.weatherFailed?"Погода недоступна":"Погода загружается…";
            else{
                weatherLine=Weather.degrees(v.weather.temperature)+" "+Weather.description(v.weather.code);
                if(v.weatherLoading)weatherLine+=" ↻";
                else if(v.weatherFailed||v.now()-v.weather.updated>=Weather.FRESH_MS)weatherLine+=" · сохранено";
            }
            float y=showClock?330:393;
            v.icon(c,v.weather!=null&&v.weather.code==0?"sun":"cloud",772,y-11,25,0xffe8f4ff);
            v.text(c,v.ellipsize(weatherLine,770,28),802,y,28,0xffe8f4ff,v.regular);
        }
        if(showClock){
            String clockText=new SimpleDateFormat(v.store.bool("clock24",true)?"HH:mm":"h:mm",Locale.US).format(date);
            float size=238*v.store.number("clockSize",100)/100f;
            size=Math.max(110,Math.min(320,size));
            Paint p=v.paint;
            p.setShader(null);p.setColorFilter(null);p.setStyle(Paint.Style.FILL);
            p.setTypeface(v.light);p.setTextSize(size);p.setTextAlign(Paint.Align.CENTER);
            p.setColor(0xdfffffff);p.setAlpha(255);
            p.setShadowLayer(13,0,1,0x9aeea0ff);
            c.drawText(clockText,960,599,p);
            p.clearShadowLayer();p.setTextAlign(Paint.Align.LEFT);
        }
        RectF clockArea=new RectF(570,245,1350,628);
        if(v.clockFocused&&v.screen==GlassView.Screen.HOME)
            v.round(c,clockArea,20,0x08ffffff,0x75ffffff,1.5f);
        if(v.screen==GlassView.Screen.HOME&&(showClock||v.store.bool("showWeather",true)))
            v.hits.add(new GlassView.Hit(clockArea,"clock",0));

        if(SystemClock.uptimeMillis()-networkChecked>=3000){
            network=v.host.networkLabel();networkChecked=SystemClock.uptimeMillis();
        }
        boolean connected=network.startsWith("Подключено")||network.equals("Есть подключение");
        boolean cable=network.contains("кабелю");
        topButton(c,new RectF(1084,82,1314,145),"input","Источники",0,false);
        RectF net=new RectF(1328,82,1550,145);
        boolean active=v.topFocused&&v.topIndex==1&&v.screen==GlassView.Screen.HOME;
        v.round(c,net,32,active?0x415d8ec7:0x2b203f72,
            active?0xffe8f4ff:0x70bfe7ff,active?2:1);
        premiumEdge(c,net,32,0xff5aaaff,active);
        v.icon(c,"wifi",1357,113,25,GlassView.WHITE);
        v.text(c,cable?"LAN":"Wi-Fi",1382,122,21,GlassView.WHITE,v.regular);
        v.round(c,new RectF(1470,102,1532,126),12,
            connected?0xff22d78c:0xff485365,0,0);
        v.text(c,connected?"ON":"OFF",1501,120,15,
            connected?0xff07271b:0xffe1e7ef,v.medium,Paint.Align.CENTER);
        if(v.screen==GlassView.Screen.HOME)v.hits.add(new GlassView.Hit(net,"top",1));
        topButton(c,new RectF(1564,82,1627,145),"timer","",2,false);
        topButton(c,new RectF(1640,82,1703,145),"hourglass","",3,false);
        topButton(c,new RectF(1714,82,1777,145),"tvgear","",4,false);
        topButton(c,new RectF(1790,82,1853,145),"gear","",5,false);
    }
    /** Top-left prayer strip, aligned with the controls at the right. */
    void drawPremiumPrayers(Canvas c){
        PrayerTimes.Display value=v.host.prayers.display(v.now());
        RectF bar=new RectF(73,86,800,174);
        v.round(c,bar,23,0x3c08183d,0x8bb6d6ff,1.4f);
        Paint p=v.paint;
        p.setShader(new LinearGradient(bar.left,bar.top,bar.right,bar.bottom,
            new int[]{0x20ffffff,0x00000000,0x229a73fe},null,Shader.TileMode.CLAMP));
        c.drawRoundRect(bar,23,23,p);p.setShader(null);
        String heading="Махачкала · "+new SimpleDateFormat("d MMMM",new Locale("ru")).format(new Date(v.now()))+" · Sajda";
        v.text(c,heading,436,73,18,0xffedf5ff,v.regular,Paint.Align.CENTER);
        if(value==null){
            v.text(c,"Обновите расписание Sajda",436,138,21,GlassView.WHITE,v.medium,Paint.Align.CENTER);
        }else for(int i=0;i<6;i++){
            float colWidth=bar.width()/6;
            float cx=bar.left+(i+.5f)*colWidth;
            boolean focus=i==value.active;
            if(focus){
                RectF r=new RectF(bar.left+i*colWidth+3,90,
                    bar.left+(i+1)*colWidth-3,169);
                v.round(c,r,17,0x804a76e8,0xdd31e6ff,1.8f);
                p.setShader(new RadialGradient(cx,168,67,
                    new int[]{0x9600e7ff,0x2400a3ff,Color.TRANSPARENT},
                    new float[]{0,.26f,1},Shader.TileMode.CLAMP));
                c.drawRect(cx-65,154,cx+65,176,p);p.setShader(null);
            }
            v.text(c,PrayerTimes.LABELS[i],cx,120,18,
                focus?0xff9cf6ff:0xfff2f4ff,v.regular,Paint.Align.CENTER);
            v.text(c,value.day.times[i],cx,153,28,
                focus?0xff68f7ff:GlassView.WHITE,v.medium,Paint.Align.CENTER);
        }
        if(v.prayerFocused&&v.screen==GlassView.Screen.HOME)
            v.round(c,bar,23,Color.TRANSPARENT,GlassView.WHITE,2f);
        if(v.screen==GlassView.Screen.HOME)
            v.hits.add(new GlassView.Hit(bar,"prayer",0));
    }
''')

once(C,
'''        if(v.showPrayer()){prayerGlass(c);v.drawPrayers(c);}
        if(v.recentFocused&&v.hasRecents())recents(c);''',
'''        if(v.showPrayer())drawPremiumPrayers(c);''')
# A removed shelf must also disappear from remote navigation in the ambient look.
once(G,
'''    boolean hasRecents(){return (ambient()||couch())&&store.bool("showRecents",true)&&!shelfCards().isEmpty();}''',
'''    boolean hasRecents(){return couch()&&store.bool("showRecents",true)&&!shelfCards().isEmpty();}''')

# Raise the complete dock by roughly 6% of TV height while keeping the + tile.
once(C,
'''        v.round(c,new RectF(56,786,1865,1050),30,0x1007102b,0x1dffffff,1);''',
'''        v.round(c,new RectF(56,713,1865,1017),30,0x1007102b,0x1dffffff,1);''')
once(C,
'''        v.text(c,(v.moving?"↔  ":"")+v.ellipsize(name,1600,58),84,750,58,GlassView.WHITE,v.regular);''',
'''        v.text(c,(v.moving?"↔  ":"")+v.ellipsize(name,1600,58),84,697,58,GlassView.WHITE,v.regular);''')
once(C,
'''        c.save();c.clipRect(60,774,1860,1065);''',
'''        c.save();c.clipRect(60,730,1860,1022);''')
once(C,
'''RectF normal=new RectF(x,812,x+size,812+height),r=new RectF(normal);''',
'''RectF normal=new RectF(x,754,x+size,754+height),r=new RectF(normal);''')
once(C,
'''hit.intersect(72,786,1848,1000)''',
'''hit.intersect(72,730,1848,965)''')
once(C,
'''if(apps.isEmpty())v.text(c,"Выберите +, чтобы добавить приложение на панель",84,788,23,0xffa6b2c6,v.regular);''',
'''if(apps.isEmpty())v.text(c,"Выберите +, чтобы добавить приложение на панель",84,732,23,0xffa6b2c6,v.regular);''')
# Apply configured or automatically detected focus hue to the dock glow.
once(C,
'''            int accent=i<apps.size()?apps.get(i).accent:0xffb9c8d9;''',
'''            int accent=i<apps.size()?(selected?selectedColor():apps.get(i).accent):0xffb9c8d9;''')
# Keep deep blues but enrich orange glow around the setting sun on the same photo.
once(C,
'''        // Dark glass-safe regions at top and dock; keep middle panorama vivid.''',
'''        // Gentle warm glow around the sun and reflection, without changing the photo.
        if(picture!=null&&!picture.isRecycled()&&v.store.bool("sunsetBackground",true)){
            p.setShader(new RadialGradient(1560,565,555,
                new int[]{0x22ffbf51,0x12ff7046,Color.TRANSPARENT},
                new float[]{0,.34f,1},Shader.TileMode.CLAMP));
            c.drawRect(840,40,1920,1080,p);p.setShader(null);
        }
        // Dark glass-safe regions at top and dock; keep middle panorama vivid.''')
# Less darkening of dramatic vivid backdrop in the upper half.
once(C,
'''new int[]{0x88010a23,0x3a06122b,0x06000000,0x20030a1d,0x9d030b20},''',
'''new int[]{0x76010a23,0x2606122b,0x00000000,0x16030a1d,0x86030b20},''')
once(B,"versionCode 20","versionCode 21")
once(B,"versionName '1.3.9'","versionName '1.3.10'")
s=C.read_text(encoding="utf-8")
assert 'drawPremiumPrayers(c)' in s and 'prayerGlass(c);v.drawPrayers(c);' not in s
assert 'recents(c);' not in s.split('    void draw(Canvas c){',1)[1].split('    void header(Canvas c){',1)[0]
assert 'new RectF(x,754' in s
assert 'topButton(c,new RectF(1790,82,1853,145)' in s
assert 'premiumReflection(c,r,apps.get(i),selected)' in s
assert 'sunset-premium.webp' in s
assert 'launchTvTimer' in G.read_text(encoding="utf-8")
print("BraviaGlass 1.3.10: centered clock and weather, top-left Sajda, raised dock, no Continue Watching in ambient home.")
