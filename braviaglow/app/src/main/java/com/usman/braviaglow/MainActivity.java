package com.usman.braviaglow;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public final class MainActivity extends Activity {
    private SharedPreferences prefs;
    private LinearLayout panel;
    private Button autoButton, intensityButton;
    private TextView status;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        prefs=getSharedPreferences("glow",MODE_PRIVATE);
        ScrollView scroll=new ScrollView(this);
        LinearLayout outer=new LinearLayout(this);
        outer.setGravity(Gravity.CENTER);
        outer.setOrientation(LinearLayout.VERTICAL);
        outer.setPadding(dp(36),dp(24),dp(36),dp(24));
        outer.setBackground(new GradientDrawable(GradientDrawable.Orientation.TL_BR,
            new int[]{0xff091422,0xff123048,0xff0b1420}));
        panel=new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(-1,-2);
        pp.width=dp(850);
        outer.addView(panel,pp);
        scroll.addView(outer);
        setContentView(scroll);

        addText("BraviaGlow 0.4 · диагностика Sony",32,Color.WHITE);
        addText("Оригинальный Android TV Home остаётся без изменений.",20,0xffd2e8f4);
        addText("Важное изменение: цветной эффект выключен по умолчанию. Сначала проверь короткое нажатие OK без эффекта.",17,0xffc0d0df);

        autoButton=addButton("",()->{
            boolean enabled=prefs.getBoolean("experimental_enabled",false);
            if(enabled) {
                prefs.edit().putBoolean("experimental_enabled",false).apply();
                refresh();
            } else {
                new AlertDialog.Builder(this)
                    .setTitle("Пробный автоматический режим")
                    .setMessage("Включает плавную цветную подсветку при распознавании приложений в Sony Home. Нужна служба специальных возможностей. На некоторых Sony она может менять поведение кнопки OK. Если появится меню вместо запуска приложения — сразу выключите этот режим и саму службу специальных возможностей.")
                    .setNegativeButton("Отмена",(d,w)->{})
                    .setPositiveButton("Включить тест",(d,w)->{
                        prefs.edit().putBoolean("experimental_enabled",true).apply();
                        refresh();
                    }).show();
            }
        });
        intensityButton=addButton("",()->{
            int next=(prefs.getInt("intensity",0)+1)%3;
            prefs.edit().putInt("intensity",next).apply();
            refresh();
        });
        status=addText("",18,0xffe4f3ff);
        addButton("Проверить красный градиент (2 секунды)",()->{
            if (!prefs.getBoolean("service_connected",false)) {
                new AlertDialog.Builder(this).setTitle("Служба не подключена")
                    .setMessage("Включи службу BraviaGlow в специальных возможностях Sony. Пока служба не подключена, тестовый градиент показать невозможно.")
                    .setPositiveButton("Понятно",(d,w)->{}).show();
                return;
            }
            prefs.edit().putInt("demo_sequence",prefs.getInt("demo_sequence",0)+1).apply();
            refresh();
        });
        addButton("Проверить состояние",this::refresh);
        addText("Как активировать: Настройки Sony → Настройки устройства → Специальные возможности → BraviaGlow. Если пункта нет, использование ADB — только с вашего разрешения. Эта кнопка не пытается открыть неподдерживаемые настройки.",16,0xffa9c0d5);
        addText("Если красный градиент работает, но событий Sony Home по-прежнему 0 — проблема в распознавании фокуса, а не в цветном слое.",16,0xffb8d3e3);
        addText("Приложение не перехватывает кнопки пульта и не вызывает действия с интерфейсом. Но сама служба специальных возможностей на старом Sony может повлиять на поведение OK.",16,0xffa9c0d5);
        addButton("Закрыть BraviaGlow",this::finish);
        refresh();
    }

    private void refresh() {
        boolean on=prefs.getBoolean("experimental_enabled",false);
        autoButton.setText(on?"Автоматический эффект: ВКЛ · Выключить":"Автоматический эффект: ВЫКЛ · Безопасный режим");
        String[] levels={"Очень мягкий","Мягкий","Заметный"};
        intensityButton.setText("Яркость: "+levels[prefs.getInt("intensity",0)]);
        String detail=prefs.getString("last_event","Пока нет событий от Sony Home");
        boolean connected=prefs.getBoolean("service_connected",false);
        status.setText("Служба: "+(connected?"подключена":"не подключена")+
            "\nСобытий от Sony Home: "+prefs.getInt("home_events",0)+
            "\nПоследний тип: "+prefs.getString("last_event_type","нет")+
            "\nПоследнее событие: "+detail);
    }
    @Override protected void onResume(){super.onResume();if(status!=null)refresh();}
    private TextView addText(String s,int size,int color){
        TextView v=new TextView(this);
        v.setText(s);v.setTextColor(color);v.setTextSize(size);
        v.setPadding(0,dp(7),0,dp(7));
        panel.addView(v,new LinearLayout.LayoutParams(-1,-2));
        return v;
    }
    private Button addButton(String text,Runnable action) {
        Button b=new Button(this);
        b.setText(text);b.setTextSize(17);b.setAllCaps(false);
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(57));
        p.topMargin=dp(8);
        panel.addView(b,p);
        b.setOnClickListener(v->action.run());
        return b;
    }
    private int dp(int v){return Math.round(v*getResources().getDisplayMetrics().density);}
}
