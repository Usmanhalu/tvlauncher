package com.usman.braviaglow;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public class MainActivity extends Activity {
    private LinearLayout panel;
    private TextView lastEvent;
    private Button intensityButton;
    private SharedPreferences prefs;

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences("glow", MODE_PRIVATE);
        ScrollView scroller = new ScrollView(this);
        LinearLayout base = new LinearLayout(this);
        base.setOrientation(LinearLayout.VERTICAL);
        base.setGravity(Gravity.CENTER);
        base.setPadding(dp(45), dp(36), dp(45), dp(36));
        GradientDrawable bg = new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                new int[]{0xff0a1323, 0xff14283d, 0xff080c14});
        base.setBackground(bg);
        panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(20), dp(12), dp(20), dp(12));
        LinearLayout.LayoutParams pp = new LinearLayout.LayoutParams(-1, -2);
        pp.width = dp(820);
        base.addView(panel, pp);
        scroller.addView(base);
        setContentView(scroller);

        text("BraviaGlow · Тест 0.2", 34, 0xffffffff);
        text("Плавный градиент без тёмных полос на оригинальном Sony Android TV Home.", 20, 0xffd4e5f2);
        text("Это дополнение, НЕ новый лаунчер. Никаких изменений системных файлов и root.", 17, 0xff8ca4bb);
        addButton("1. Включить BraviaGlow в специальных возможностях", () -> {
            Intent i = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
            try { startActivity(i); } catch (Exception ex) {
                text("Меню специальных возможностей недоступно: откройте его в настройках Sony.", 17, 0xffffbbaa);
            }
        });
        intensityButton = addButton("", () -> {
            int next = (prefs.getInt("intensity", 1) + 1) % 3;
            prefs.edit().putInt("intensity", next).apply();
            refreshIntensity();
        });
        lastEvent = text("", 18, 0xffe0efff);
        addButton("Обновить статус", this::refreshStatus);
        addButton("Закрыть (Sony останется прежним)", this::finish);
        text("После включения службы нажимайте стрелки пульта на главном экране. Подсветка должна исчезать при запуске приложений.", 18, 0xffafc5db);
        text("Если не нравится, отключите службу BraviaGlow в разделе «Специальные возможности». Данные с экрана не отправляются в интернет.", 16, 0xff92a5b7);
        refreshIntensity();
        refreshStatus();
    }

    private void refreshIntensity() {
        String[] levels = {"Слабая", "Средняя", "Заметная"};
        intensityButton.setText("2. Интенсивность: " + levels[prefs.getInt("intensity", 1)]);
    }
    @Override public void onResume() { super.onResume(); if (lastEvent != null) refreshStatus(); }
    private void refreshStatus() {
        String detail = prefs.getString("last_event", "Пока нет событий от Sony Home");
        lastEvent.setText("Последнее событие: " + detail);
    }
    private TextView text(String value, int size, int color) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextSize(size);
        t.setTextColor(color);
        t.setPadding(0, dp(10), 0, dp(10));
        panel.addView(t, new LinearLayout.LayoutParams(-1, -2));
        return t;
    }
    private Button addButton(String label, Runnable click) {
        Button b = new Button(this);
        b.setText(label);
        b.setTextSize(19);
        b.setAllCaps(false);
        b.setTextColor(Color.WHITE);
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, dp(58));
        p.topMargin = dp(12);
        panel.addView(b, p);
        b.setOnClickListener(v -> click.run());
        return b;
    }
    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
}
