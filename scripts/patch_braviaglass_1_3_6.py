#!/usr/bin/env python3
"""BraviaGlass v1.3.6: real TV input picker, separate Sony/launcher settings,
and move date/weather under greeting and clock on ColorHome.

Apply after v1.3.2, v1.3.3, v1.3.4, and v1.3.5 patches.
The existing package name, signing, profiles, prayer times, dock and updater are intact.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else ".")
java=root/"app/src/main/java/com/usman/braviaglass"
M=java/"MainActivity.java"
G=java/"GlassView.java"
C=java/"ColorHome.java"
B=root/"app/build.gradle"

def replace(file,old,new):
    text=file.read_text(encoding="utf-8")
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f"{file.name}: expected exactly one match for {old[:120]!r}, found {n}")
    file.write_text(text.replace(old,new,1),encoding="utf-8")

replace(M,
'    void inputs(){system(new Intent("com.sony.dtv.intent.action.TVINPUT"),new Intent("android.intent.action.VIEW").setData(Uri.parse("content://android.media.tv/passthrough")),new Intent("android.settings.TV_INPUT_SETTINGS"));}',
'''    /**
     * On Sony Android 9 the old implicit Sony TVINPUT Intent can open the
     * device Settings panel instead of the physical source chooser.
     * Enumerate the real hardware passthrough inputs instead; never fall back
     * to a generic Settings screen for the Sources shortcut.
     */
    void inputs(){
        final java.util.ArrayList<android.media.tv.TvInputInfo> ports=new java.util.ArrayList<>();
        try{
            android.media.tv.TvInputManager tv=(android.media.tv.TvInputManager)getSystemService(android.content.Context.TV_INPUT_SERVICE);
            if(tv!=null)for(android.media.tv.TvInputInfo info:tv.getTvInputList()){
                if(info!=null&&info.isPassthroughInput())ports.add(info);
            }
        }catch(RuntimeException ex){
            glass.notifyText("Не удалось прочитать список HDMI и других входов Sony");
            return;
        }
        if(ports.isEmpty()){
            glass.notifyText("Sony не предоставил список входов. Используйте INPUT на пульте");
            return;
        }
        final String[] labels=new String[ports.size()];
        for(int n=0;n<ports.size();n++){
            android.media.tv.TvInputInfo info=ports.get(n);
            String label="";
            try{
                CharSequence name=info.loadLabel(this);
                if(name!=null)label=name.toString().trim();
            }catch(RuntimeException ignored){}
            if(label.isEmpty()){
                switch(info.getType()){
                    case android.media.tv.TvInputInfo.TYPE_HDMI:label="HDMI";break;
                    case android.media.tv.TvInputInfo.TYPE_COMPONENT:label="Компонентный вход";break;
                    case android.media.tv.TvInputInfo.TYPE_COMPOSITE:label="AV";break;
                    case android.media.tv.TvInputInfo.TYPE_VGA:label="VGA";break;
                    default:label="Вход телевизора";break;
                }
                label+=" "+(n+1);
            }
            labels[n]=label;
        }
        choice("Источники Sony TV",labels,index->{
            if(index<0||index>=ports.size())return;
            try{
                Intent watch=new Intent(Intent.ACTION_VIEW,
                    android.media.tv.TvContract.buildChannelUriForPassthroughInput(ports.get(index).getId()));
                startActivity(watch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            }catch(RuntimeException ex){
                glass.notifyText("Sony не открыл этот вход. Используйте кнопку INPUT на пульте");
            }
        });
    }
    /** Physical Sony device settings are separate from BraviaGlass settings. */
    void tvSettings(){
        try{
            Intent intent=new Intent(Settings.ACTION_SETTINGS).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        }catch(RuntimeException ex){
            glass.notifyText("Системные настройки Sony недоступны");
        }
    }''')

replace(C,
'''        float dateX=clock?Math.max(306,84+v.measure("00:00",70*v.store.number("clockSize",100)/100f)+36):84;
        String weekday=new SimpleDateFormat("EEEE",new Locale("ru")).format(date).toUpperCase(new Locale("ru"));
        v.text(c,weekday,dateX,109,19,0xffc1c9d7,v.medium);
        v.text(c,new SimpleDateFormat("d MMMM",new Locale("ru")).format(date),dateX,141,22,0xffa6b2c6,v.regular);
        if(v.store.bool("showWeather",true))weather(c,dateX);
        RectF clockArea=new RectF(72,58,Math.min(900,dateX+500),210);''',
'''        // Put date and weather *below* the clock, not to its right.
        String weekday=new SimpleDateFormat("EEEE",new Locale("ru")).format(date);
        if(!weekday.isEmpty())weekday=weekday.substring(0,1).toUpperCase(new Locale("ru"))+weekday.substring(1);
        String dateLine=weekday+" "+new SimpleDateFormat("d MMMM",new Locale("ru")).format(date);
        if(v.store.bool("showWeather",true)){
            String weatherLine;
            if(v.weather==null){
                weatherLine=v.weatherFailed?"Погода недоступна":"Погода загружается…";
            }else{
                weatherLine=Weather.degrees(v.weather.temperature)+" "+Weather.description(v.weather.code);
                if(v.weatherLoading)weatherLine+=" ↻";
                else if(v.weatherFailed||v.now()-v.weather.updated>=Weather.FRESH_MS)weatherLine+=" · сохранено";
            }
            dateLine+="   ·   "+weatherLine;
        }
        final float dateY=clock?220:125;
        v.text(c,v.ellipsize(dateLine,930,23),84,dateY,23,0xffc6d0df,v.regular);
        RectF clockArea=new RectF(72,58,1050,clock?252:165);''')

replace(C,
'''        topButton(c,new RectF(1714,82,1868,145),"gear","Настройки",4,false);''',
'''        // Dedicated Sony hardware settings, followed by icon-only launcher settings.
        topButton(c,new RectF(1714,82,1777,145),"tvgear","",4,false);
        topButton(c,new RectF(1790,82,1853,145),"gear","",5,false);''')

replace(C,
'''static final String[] TOP_LABELS={"Источники","Подключение","Timer","Таймер заставки","Настройки"};''',
'''static final String[] TOP_LABELS={"Источники","Подключение","Timer","Таймер заставки","Настройки Sony TV","Настройки BraviaGlass"};''')

replace(C,
'''if(right)v.topIndex=Math.min(4,v.topIndex+1);''',
'''if(right)v.topIndex=Math.min(5,v.topIndex+1);''')

replace(G,
'''                if(right)topIndex=Math.min(couch()?3:2,topIndex+1);''',
'''                if(right)topIndex=Math.min(ambient()?5:couch()?3:2,topIndex+1);''')

replace(G,
'''else if(topFocused)label=ambient()?ColorHome.TOP_LABELS[Math.max(0,Math.min(4,topIndex))]:couch()?''',
'''else if(topFocused)label=ambient()?ColorHome.TOP_LABELS[Math.max(0,Math.min(5,topIndex))]:couch()?''')

replace(G,
'''                    else if(topIndex==3)host.timer();
                    else open(Screen.SETTINGS);''',
'''                    else if(topIndex==3)host.timer();
                    else if(topIndex==4)host.tvSettings();
                    else open(Screen.SETTINGS);''')

replace(G,
'''            case "input":
''',
'''            case "tvgear":
                // TV display outline plus settings cog; unlike the launcher gear.
                c.drawRoundRect(new RectF(-15,-12,15,8),3,3,paint);
                c.drawLine(-5,12,5,12,paint);
                c.drawLine(0,8,0,12,paint);
                c.drawCircle(9,-7,4.3f,paint);
                break;
            case "input":
''')

replace(B,"versionCode 16","versionCode 17")
replace(B,"versionName '1.3.5'","versionName '1.3.6'")

# Prove expected safety properties of the resulting sources.
g=G.read_text(encoding="utf-8")
c=C.read_text(encoding="utf-8")
m=M.read_text(encoding="utf-8")
assert 'void tvSettings()' in m
assert 'TvContract.buildChannelUriForPassthroughInput' in m
assert 'else if(topIndex==4)host.tvSettings();' in g
assert '"Настройки Sony TV","Настройки BraviaGlass"' in c
assert '"gear","",5,false' in c
assert 'final float dateY=clock?220:125' in c
assert 'host.prayerSettings()' in g
assert 'else if(ambient())openAddPicker();' in g
print("BraviaGlass 1.3.6: TV inputs picker, separate Sony settings, compact icon-only launcher gear, date/weather under clock.")
