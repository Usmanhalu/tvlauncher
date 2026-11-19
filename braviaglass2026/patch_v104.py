from pathlib import Path
root=Path('app/src/main/java/com/braviaglass/tv')
p=root/'LauncherActivity.java'
t=p.read_text()
def change(a,b):
    global t
    if a not in t: raise RuntimeError('Cannot find fragment: '+a[:95])
    t=t.replace(a,b)
change('    private final Runnable dataTick=new Runnable()', '''    private final Runnable wallpaperTick=new Runnable(){@Override public void run(){
        if(pref!=null && scene!=null){
            long minutes=pref.getInt("wallpaper_interval",30);
            if(minutes>0){
                long now=System.currentTimeMillis();
                long last=0;
                try{last=Long.parseLong(pref.get("wallpaper_changed_at","0"));}catch(Exception ignored){}
                if(last<=0 || now<last)pref.put("wallpaper_changed_at",String.valueOf(now));
                else if(now-last>=minutes*60000L){
                    pref.putInt("scene",(pref.getInt("scene",0)+1)%4);
                    pref.put("wallpaper_changed_at",String.valueOf(now));
                    scene.setScene(pref.getInt("scene",0));
                }
            }
        }
        handler.postDelayed(this,60000L);
    }};
    private final Runnable dataTick=new Runnable()''')
change('        handler.post(dataTick);','        handler.post(dataTick);\n        handler.post(wallpaperTick);')
change('pageContainer.addView(hero,new LinearLayout.LayoutParams(-1,dp(92)));','pageContainer.addView(hero,new LinearLayout.LayoutParams(-1,dp(170)));')
change('buttonInto(actions,"Быстрые настройки  ⚙",()->quickSettings());','')
change('buttonInto(actions,"Сортировка  ⇅",()->chooseSort());','')
change('TextView label=text("ИЗБРАННЫЕ ПРИЛОЖЕНИЯ",14,WHITE,true);','TextView label=text("Ваши приложения",17,WHITE,true);')
change('heading.addView(label,new LinearLayout.LayoutParams(0,-1,1));','''heading.addView(label,new LinearLayout.LayoutParams(0,-1,1));
        TextView sortHome=action("Сортировка  ⇅",()->chooseSort());
        LinearLayout.LayoutParams sh=new LinearLayout.LayoutParams(dp(144),dp(34));sh.rightMargin=dp(10);
        heading.addView(sortHome,sh);
        TextView editHome=action("Изменить  ✎",()->showPage("apps"));
        heading.addView(editHome,new LinearLayout.LayoutParams(dp(129),dp(34)));''')
change('int diameter=compact?64:76;','int diameter=compact?72:92;')
change('card.setBackground(bg(Color.argb(75,12,30,52),18,0));','card.setBackground(bg(Color.argb(30,12,22,36),18,0));')
change('icon.setPadding(dp(5),dp(5),dp(5),dp(5));','icon.setPadding(dp(2),dp(2),dp(2),dp(2));')
change('dp(compact?116:120),dp(compact?128:136)','dp(compact?118:132),dp(compact?128:144)')
change('TextView edit=action("Изменить +",()->showPage("apps"));','TextView edit=action("+",()->showPage("apps"));')
change('setting("Фон главного экрана","Горы, горизонт или город",()->chooseScene());', '''setting("Фон главного экрана","Горы, море, город или лес",()->chooseScene());
        setting("Автосмена обоев",wallpaperIntervalName(pref.getInt("wallpaper_interval",30)),()->chooseWallpaperInterval());''')
change('private void chooseScene(){String[] names={"Синие горы","Тёплый горизонт","Городские огни"};\n        new AlertDialog.Builder(this).setTitle("Фон").setSingleChoiceItems(names,pref.getInt("scene",0),(d,w)->{pref.putInt("scene",w);d.dismiss();showPage("settings");}).setNegativeButton("Отмена",null).show();', '''private void chooseScene(){String[] names={"Горное озеро","Морское побережье","Ночной город","Туманный лес"};
        new AlertDialog.Builder(this).setTitle("Обои").setSingleChoiceItems(names,pref.getInt("scene",0),(d,w)->{
            pref.putInt("scene",w);pref.put("wallpaper_changed_at",String.valueOf(System.currentTimeMillis()));
            d.dismiss();showPage("settings");}).setNegativeButton("Отмена",null).show();''')
change('    private void chooseSaver(){', '''    private String wallpaperIntervalName(int m){return m==0?"Выключена":m<60?m+" минут":m==60?"Каждый час":m==360?"Каждые 6 часов":"Раз в сутки";}
    private void chooseWallpaperInterval(){
        final int[] intervals={0,15,30,60,360,1440};
        final String[] labels={"Не менять автоматически","Каждые 15 минут","Каждые 30 минут","Каждый час","Каждые 6 часов","Раз в сутки"};
        new AlertDialog.Builder(this).setTitle("Автоматическая смена обоев")
            .setSingleChoiceItems(labels,-1,(d,w)->{
                pref.putInt("wallpaper_interval",intervals[w]);
                pref.put("wallpaper_changed_at",String.valueOf(System.currentTimeMillis()));
                d.dismiss();showPage("settings");
            }).setNegativeButton("Отмена",null).show();
    }
    private void chooseSaver(){''')
change('saverScene.setScene((pref.getInt("scene",0)+1)%3)','saverScene.setScene((pref.getInt("scene",0)+1)%4)')
change('"BraviaGlass 2026 · v1.0.3 · Собственный интерфейс, не официальное приложение Sony"','"BraviaGlass 2026 · v1.0.4 · Интерфейс неофициальный, не разработан Sony"')
change('String[] names={"Кинозал","Ночной экран","Городские огни"};','String[] names={"Горное озеро","Морское побережье","Ночной город","Туманный лес"};')
change('String[] details={"Синие горы и мягкий свет","Тёплый горизонт","Холодные городские оттенки"};','String[] details={"Закат над озером","Побережье в сумерках","Ночные огни","Лес в тумане"};')
change('for(int i=0;i<3;i++){','for(int i=0;i<4;i++){')
change('"Нажмите OK для запуска. Удерживайте OK для избранного."','"Выберите программу для запуска или добавления в избранное."')
p.write_text(t)
p=root/'AppRepository.java'
t=p.read_text()
t=t.replace('try { icon=ri.loadIcon(pm); } catch(Exception ex){ icon=c.getDrawable(android.R.drawable.sym_def_app_icon); }',
'''try { icon=pm.getApplicationIcon(ai.packageName); }
                catch(Exception ex){
                    try{ icon=ri.loadIcon(pm); }
                    catch(Exception ex2){ icon=c.getDrawable(android.R.drawable.sym_def_app_icon); }
                }''')
p.write_text(t)
p=Path('app/build.gradle')
t=p.read_text().replace('com.braviaglass.tv2026.v103','com.braviaglass.tv2026.v104').replace('versionCode 4','versionCode 5').replace("versionName '1.0.3'","versionName '1.0.4'")
p.write_text(t)
p=Path('app/src/main/AndroidManifest.xml')
t=p.read_text().replace('com.braviaglass.tv2026.v103','com.braviaglass.tv2026.v104').replace('BraviaGlass 2026 v1.0.3','BraviaGlass 2026 v1.0.4')
p.write_text(t)
print('Updated BraviaGlass v1.0.4 with rotating wallpapers')
