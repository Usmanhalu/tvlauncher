package com.usman.braviaglow;

import android.accessibilityservice.AccessibilityService;
import android.animation.ValueAnimator;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.graphics.RadialGradient;
import android.graphics.Rect;
import android.graphics.Shader;
import android.graphics.drawable.Drawable;
import android.os.Build;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public final class GlowAccessibilityService extends AccessibilityService {
    private static final String TAG = "BraviaGlow";
    private static final String HOME_PACKAGE = "com.google.android.tvlauncher";
    private WindowManager windowManager;
    private GlowView glowView;
    private boolean overlayAdded;
    private boolean homeVisible;
    private final Map<String, Integer> colorCache = new HashMap<>();
    private String lastLabel = "";

    @Override protected void onServiceConnected() {
        super.onServiceConnected();
        try {
            windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
            glowView = new GlowView();
            int flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |
                        WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE |
                        WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN;
            WindowManager.LayoutParams p = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
                flags, PixelFormat.TRANSLUCENT);
            p.gravity = Gravity.TOP | Gravity.START;
            windowManager.addView(glowView, p);
            overlayAdded = true;
            glowView.setVisibility(View.GONE);
            getSharedPreferences("glow", MODE_PRIVATE).edit()
                .putString("last_event", "Служба подключена; откройте Sony Home и переместите фокус").apply();
            Log.i(TAG, "Accessibility overlay started");
        } catch (Exception ex) {
            Log.e(TAG, "Could not add accessibility overlay", ex);
            getSharedPreferences("glow", MODE_PRIVATE).edit()
                .putString("last_event", "Не удалось запустить подсветку: " + ex.getClass().getSimpleName()).apply();
        }
    }

    @Override public void onAccessibilityEvent(AccessibilityEvent e) {
        if (!overlayAdded || e == null) return;
        try {
            CharSequence eventPackage = e.getPackageName();
            String pkg = eventPackage == null ? "" : eventPackage.toString();
            int eventType = e.getEventType();

            if (eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
                if (HOME_PACKAGE.equals(pkg)) {
                    homeVisible = true;
                    showOverlay();
                } else if (!pkg.equals("com.android.systemui") && !pkg.equals(getPackageName())) {
                    homeVisible = false;
                    glowView.setVisibility(View.GONE);
                }
            }

            if (!HOME_PACKAGE.equals(pkg)) return;
            if (eventType != AccessibilityEvent.TYPE_VIEW_FOCUSED &&
                eventType != AccessibilityEvent.TYPE_VIEW_ACCESSIBILITY_FOCUSED) return;

            homeVisible = true;
            showOverlay();
            AccessibilityNodeInfo source = e.getSource();
            String title = findAppName(e, source);
            if (title.isEmpty()) return;
            Rect rect = new Rect();
            if (source != null) source.getBoundsInScreen(rect);
            float x = rect.width() > 0 ? rect.exactCenterX() : getResources().getDisplayMetrics().widthPixels * 0.5f;

            String key = title.toLowerCase(Locale.ROOT);
            int color = mapColor(key);
            if (color == 0) {
                Integer cached = colorCache.get(key);
                if (cached == null) {
                    cached = findInstalledAppColor(title);
                    colorCache.put(key, cached);
                }
                color = cached;
            }
            glowView.animateTo(color, x);
            if (!title.equals(lastLabel)) {
                lastLabel = title;
                getSharedPreferences("glow", MODE_PRIVATE).edit()
                    .putString("last_event", "Фокус: " + title + "; цвет #" + String.format(Locale.US, "%06X", color & 0xffffff)).apply();
                Log.d(TAG, "Focus: " + title);
            }
        } catch (Exception ex) {
            Log.e(TAG, "Accessibility event error", ex);
        }
    }

    private void showOverlay() {
        if (homeVisible && glowView.getVisibility() != View.VISIBLE) {
            glowView.setVisibility(View.VISIBLE);
        }
    }

    private String findAppName(AccessibilityEvent event, AccessibilityNodeInfo node) {
        for (CharSequence text : event.getText()) {
            if (text != null && text.length() > 0) return text.toString().trim();
        }
        AccessibilityNodeInfo current = node;
        for (int depth = 0; depth < 3 && current != null; depth++) {
            CharSequence desc = current.getContentDescription();
            if (desc != null && desc.length() > 0) return desc.toString().trim();
            CharSequence text = current.getText();
            if (text != null && text.length() > 0) return text.toString().trim();
            for (int i = 0; i < Math.min(4, current.getChildCount()); i++) {
                AccessibilityNodeInfo child = current.getChild(i);
                if (child == null) continue;
                CharSequence childDesc = child.getContentDescription();
                CharSequence childText = child.getText();
                if (childDesc != null && childDesc.length() > 0) return childDesc.toString().trim();
                if (childText != null && childText.length() > 0) return childText.toString().trim();
            }
            current = current.getParent();
        }
        return "";
    }

    private int mapColor(String name) {
        if (name.contains("youtube") || name.contains("ютуб")) return Color.rgb(236, 42, 43);
        if (name.contains("zona") || name.contains("зона")) return Color.rgb(18, 196, 183);
        if (name.contains("iptv")) return Color.rgb(34, 126, 246);
        if (name.contains("vlc")) return Color.rgb(255, 146, 30);
        if (name.contains("vokino")) return Color.rgb(140, 90, 240);
        if (name.contains("netflix")) return Color.rgb(220, 36, 42);
        if (name.contains("google play") || name.contains("play store")) return Color.rgb(67, 178, 125);
        if (name.contains("send files")) return Color.rgb(37, 201, 205);
        if (name.contains("главная") || name.contains("приложения") ||
            name.contains("настройки") || name.contains("поиск")) return Color.rgb(49, 99, 160);
        return 0;
    }

    private int findInstalledAppColor(String label) {
        try {
            PackageManager pm = getPackageManager();
            Intent i = new Intent(Intent.ACTION_MAIN);
            i.addCategory(Intent.CATEGORY_LEANBACK_LAUNCHER);
            List<ResolveInfo> apps = pm.queryIntentActivities(i, 0);
            for (ResolveInfo app : apps) {
                if (!label.equalsIgnoreCase(String.valueOf(app.loadLabel(pm)))) continue;
                Drawable icon = app.loadIcon(pm);
                if (icon == null) break;
                Bitmap b = Bitmap.createBitmap(32, 32, Bitmap.Config.ARGB_8888);
                Canvas canvas = new Canvas(b);
                icon.setBounds(0, 0, 32, 32);
                icon.draw(canvas);
                float sumR=0, sumG=0, sumB=0, sumWeight=0;
                float[] hsv = new float[3];
                for (int y=0; y<32; y+=2) for (int x=0; x<32; x+=2) {
                    int pixel = b.getPixel(x, y);
                    if (Color.alpha(pixel) < 80) continue;
                    Color.colorToHSV(pixel, hsv);
                    if (hsv[1] < 0.28f || hsv[2] < 0.20f) continue;
                    float weight = hsv[1]*hsv[2];
                    sumWeight+=weight;
                    sumR+=Color.red(pixel)*weight;
                    sumG+=Color.green(pixel)*weight;
                    sumB+=Color.blue(pixel)*weight;
                }
                b.recycle();
                if (sumWeight > 0) return Color.rgb(
                        Math.min(255, Math.round(sumR/sumWeight)),
                        Math.min(255, Math.round(sumG/sumWeight)),
                        Math.min(255, Math.round(sumB/sumWeight)));
                break;
            }
        } catch (Exception ignored) { }
        return Color.rgb(44, 106, 170);
    }

    @Override public void onInterrupt() {}
    @Override public void onDestroy() {
        try {
            if (windowManager != null && glowView != null && overlayAdded) windowManager.removeView(glowView);
        } catch (Exception ignored) {}
        super.onDestroy();
    }

    private final class GlowView extends View {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private int tint = Color.rgb(44, 106, 170);
        private float centerX = 0.5f;
        private ValueAnimator animation;

        GlowView() {
            super(GlowAccessibilityService.this);
            setLayerType(View.LAYER_TYPE_HARDWARE, null);
        }
        void animateTo(int newTint, float absoluteX) {
            int w = getWidth() > 0 ? getWidth() : getResources().getDisplayMetrics().widthPixels;
            centerX = Math.max(.13f, Math.min(.87f, absoluteX / Math.max(w, 1)));
            if (newTint == tint) { invalidate(); return; }
            if (animation != null) animation.cancel();
            animation = ValueAnimator.ofArgb(tint, newTint);
            animation.setDuration(220);
            animation.addUpdateListener(a -> {
                tint = (int) a.getAnimatedValue();
                invalidate();
            });
            animation.start();
        }
        @Override protected void onDraw(Canvas canvas) {
            super.onDraw(canvas);
            int w = getWidth(), h = getHeight();
            if (w <= 0 || h <= 0) return;

            // One continuous full-screen wash. The previous two clipped bands
            // left a dark horizontal stripe across the center of Sony Home.
            // Low alpha preserves text, applications, and TV contrast.
            int level = getSharedPreferences("glow", MODE_PRIVATE).getInt("intensity", 1);
            int strength = level == 0 ? 28 : level == 1 ? 49 : 73;
            int r = Color.red(tint), g = Color.green(tint), b = Color.blue(tint);
            float cx = w * centerX;

            // Tint is strongest near the selected app and fades in all
            // directions without any rectangular clipping or hard edges.
            float radius = (float) Math.hypot(w, h) * 0.91f;
            paint.setShader(new RadialGradient(cx, h * 0.47f, radius,
                new int[]{
                    Color.argb(strength, r, g, b),
                    Color.argb(Math.round(strength * .69f), r, g, b),
                    Color.argb(Math.round(strength * .30f), r, g, b),
                    Color.TRANSPARENT
                },
                new float[]{0f, .38f, .70f, 1f},
                Shader.TileMode.CLAMP));
            canvas.drawRect(0, 0, w, h, paint);
            paint.setShader(null);
        }
    }
}
