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
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public final class GlowAccessibilityService extends AccessibilityService {
    private static final String TAG = "BraviaGlow";
    private static final String HOME = "com.google.android.tvlauncher";
    private WindowManager windowManager;
    private GlowView glowView;
    private SharedPreferences prefs;
    private SharedPreferences.OnSharedPreferenceChangeListener listener;
    private boolean overlayAdded;
    private final Map<String,Integer> apps = new LinkedHashMap<>();
    private String lastLabel = "";
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable hideDemo = this::hideOverlay;
    private long lastDebugAt = 0;
    private int homeEvents = 0;
    private long lastContentProbe = 0;
    private boolean demoRunning = false;

    @Override protected void onServiceConnected() {
        super.onServiceConnected();
        prefs = getSharedPreferences("glow", MODE_PRIVATE);
        windowManager = (WindowManager)getSystemService(WINDOW_SERVICE);
        glowView = new GlowView();
        buildAppColorCache();
        listener = (p,key) -> {
            if ("experimental_enabled".equals(key) && !p.getBoolean(key,false)) {
                hideOverlay();
            }
            if ("intensity".equals(key) && glowView != null) glowView.invalidate();
            if ("demo_sequence".equals(key)) showDemo();
        };
        prefs.registerOnSharedPreferenceChangeListener(listener);
        prefs.edit().putBoolean("service_connected",true)
            .putInt("home_events",0)
            .putString("last_event","Служба подключена. Проверьте тестовую подсветку.").apply();
        // Do not attach an overlay to the screen until a real app icon is focused.
        // No key filters, touch exploration, gestures or global actions are requested.
    }

    private void buildAppColorCache() {
        try {
            PackageManager pm = getPackageManager();
            Intent query = new Intent(Intent.ACTION_MAIN);
            query.addCategory(Intent.CATEGORY_LEANBACK_LAUNCHER);
            List<ResolveInfo> installed = pm.queryIntentActivities(query, 0);
            for (ResolveInfo app : installed) {
                String name = clean(String.valueOf(app.loadLabel(pm)));
                if (name.length() < 2 || apps.containsKey(name)) continue;
                Integer standard = standardColor(name);
                apps.put(name, standard != null ? standard : iconColor(app.loadIcon(pm)));
            }
        } catch (RuntimeException e) {
            Log.w(TAG, "Can't read all Android TV app names",e);
        }
    }

    @Override public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null || prefs == null) return;
        String pkg = event.getPackageName() == null ? "" : event.getPackageName().toString();
        int type = event.getEventType();
        if (HOME.equals(pkg) && type != AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED) {
            homeEvents++;
            long now = SystemClock.uptimeMillis();
            if (now - lastDebugAt > 350) {
                lastDebugAt = now;
                prefs.edit().putInt("home_events", homeEvents)
                    .putString("last_event_type", AccessibilityEvent.eventTypeToString(type)).apply();
            }
        }
        if (!prefs.getBoolean("experimental_enabled",false)) {
            // Diagnostic event counter works even in safe mode, without drawing.
            if (!demoRunning) hideOverlay();
            return;
        }

        if (type == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
            if (!HOME.equals(pkg) &&
                !"com.android.systemui".equals(pkg) &&
                !getPackageName().equals(pkg)) {
                hideOverlay();
            }
            return;
        }
        if (!HOME.equals(pkg)) return;
        if (type != AccessibilityEvent.TYPE_VIEW_FOCUSED &&
            type != AccessibilityEvent.TYPE_VIEW_ACCESSIBILITY_FOCUSED &&
            type != AccessibilityEvent.TYPE_VIEW_SELECTED &&
            type != AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED) return;
        if (type == AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED &&
            SystemClock.uptimeMillis()-lastContentProbe < 400) return;
        if (type == AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED)
            lastContentProbe = SystemClock.uptimeMillis();

        try {
            AccessibilityNodeInfo source = event.getSource();
            String label = matchAppLabel(source,event);
            Integer tint = resolveColor(label);
            if (tint == null) {
                AccessibilityNodeInfo root = getRootInActiveWindow();
                if (root != null) {
                    AccessibilityNodeInfo focused = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
                    if (focused == null)
                        focused = root.findFocus(AccessibilityNodeInfo.FOCUS_ACCESSIBILITY);
                    if (focused != null) {
                        String found = matchAppLabel(focused,event);
                        Integer matched = resolveColor(found);
                        if (matched != null) { label=found; tint=matched; }
                    }
                }
            }
            if (tint == null) {
                // Avoid painting a blue tint while focus is on search or menu items.
                // Save diagnostics to distinguish no events from unknown TV icon names.
                if (!label.isEmpty()) {
                    prefs.edit().putString("last_event",
                        "Sony Home: фокус «" + label + "», приложение не распознано").apply();
                }
                hideOverlay();
                return;
            }

            Rect bounds = new Rect();
            if (source != null) source.getBoundsInScreen(bounds);
            float x = bounds.width() > 0 ? bounds.exactCenterX() :
                      getResources().getDisplayMetrics().widthPixels * .50f;
            ensureOverlay();
            if (overlayAdded) {
                glowView.animateTo(tint,x);
                if (!label.equals(lastLabel)) {
                    lastLabel = label;
                    prefs.edit().putString("last_event", "Sony Home: " + label +
                        ", цвет #" + String.format(Locale.ROOT,"%06X",tint & 0xffffff)).apply();
                }
            }
        } catch (Exception e) {
            prefs.edit().putString("last_event",
                "Ошибка фокуса: " + e.getClass().getSimpleName()).apply();
            hideOverlay();
            Log.w(TAG,"Focus handling",e);
        }
    }

    private String clean(String value) {
        return value == null ? "" : value.toLowerCase(Locale.ROOT).trim();
    }

    private String matchAppLabel(AccessibilityNodeInfo source,AccessibilityEvent event) {
        ArrayList<String> options = new ArrayList<>();
        AccessibilityNodeInfo node = source;
        for (int depth=0; depth<3 && node!=null; depth++) {
            appendName(options,node.getContentDescription());
            appendName(options,node.getText());
            for (int i=0;i<Math.min(5,node.getChildCount());i++) {
                AccessibilityNodeInfo child = node.getChild(i);
                if (child != null) {
                    appendName(options,child.getContentDescription());
                    appendName(options,child.getText());
                }
            }
            node = node.getParent();
        }
        if (event.getContentDescription()!=null) appendName(options,event.getContentDescription());
        for (CharSequence value : event.getText()) appendName(options,value);
        for (String option:options) {
            if (resolveColor(option)!=null) return option;
        }
        return options.isEmpty() ? "" : options.get(0);
    }

    private void appendName(ArrayList<String> values,CharSequence candidate) {
        if (candidate==null) return;
        String name=candidate.toString().trim();
        if (!name.isEmpty() && name.length()<100 && !values.contains(name)) values.add(name);
    }

    private Integer resolveColor(String label) {
        if (label == null || label.isEmpty()) return null;
        String normalized=clean(label);
        Integer standard=standardColor(normalized);
        if (standard!=null) return standard;
        for (Map.Entry<String,Integer> candidate:apps.entrySet()) {
            if (normalized.equals(candidate.getKey())) return candidate.getValue();
            // Some versions of Sony Home add the word "application" to the label.
            if (normalized.startsWith(candidate.getKey()+" ")) return candidate.getValue();
        }
        return null;
    }

    private Integer standardColor(String name) {
        if (name.contains("youtube") || name.contains("ютуб")) return Color.rgb(231,41,49);
        if (name.contains("zona") || name.contains("зона")) return Color.rgb(23,177,177);
        if (name.contains("iptv")) return Color.rgb(34,116,214);
        if (name.equals("vlc") || name.contains("vlc ")) return Color.rgb(239,131,34);
        if (name.contains("vokino")) return Color.rgb(125,84,208);
        if (name.contains("netflix")) return Color.rgb(208,40,48);
        if (name.contains("google play") || name.contains("play store")) return Color.rgb(73,158,114);
        if (name.contains("send files")) return Color.rgb(32,183,188);
        return null;
    }

    private int iconColor(Drawable icon) {
        if (icon==null) return Color.rgb(57,104,152);
        Bitmap b=Bitmap.createBitmap(24,24,Bitmap.Config.ARGB_8888);
        Canvas canvas=new Canvas(b);
        icon.setBounds(0,0,24,24);
        icon.draw(canvas);
        float weight=0, r=0, g=0, bl=0;
        float[] hsv=new float[3];
        for(int y=0;y<24;y+=2) for(int x=0;x<24;x+=2) {
            int c=b.getPixel(x,y);
            if(Color.alpha(c)<120) continue;
            Color.colorToHSV(c,hsv);
            if(hsv[1]<.35f || hsv[2]<.20f) continue;
            float w=hsv[1]*hsv[2];
            weight+=w;r+=Color.red(c)*w;g+=Color.green(c)*w;bl+=Color.blue(c)*w;
        }
        b.recycle();
        return weight>0 ? Color.rgb(Math.round(r/weight),Math.round(g/weight),
                                  Math.round(bl/weight)) : Color.rgb(57,104,152);
    }

    private void ensureOverlay() {
        if (overlayAdded || windowManager==null || glowView==null) return;
        try {
            int flags=WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |
                WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE |
                WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL |
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN;
            WindowManager.LayoutParams p = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
                flags,PixelFormat.TRANSLUCENT);
            p.gravity=Gravity.START|Gravity.TOP;
            windowManager.addView(glowView,p);
            overlayAdded=true;
        } catch (RuntimeException e) {
            prefs.edit().putString("last_event",
                "Не удалось показать оверлей: "+e.getClass().getSimpleName()).apply();
            Log.w(TAG,"Overlay not supported",e);
        }
    }
    private void showDemo() {
        if (glowView == null) return;
        demoRunning = true;
        handler.removeCallbacks(hideDemo);
        ensureOverlay();
        if (overlayAdded) {
            glowView.animateTo(Color.rgb(235,44,52),
                getResources().getDisplayMetrics().widthPixels * .50f);
            prefs.edit().putString("last_event",
                "Красный градиент показан — тест слоя выполнен").apply();
        } else {
            prefs.edit().putString("last_event",
                "Тест слоя не удался: Android не разрешил оверлей").apply();
        }
        handler.postDelayed(() -> { demoRunning=false; hideOverlay(); }, 2200);
    }

    private void hideOverlay() {
        if (!overlayAdded) return;
        try {
            windowManager.removeView(glowView);
        } catch (RuntimeException e) {
            Log.w(TAG,"Overlay removal",e);
        }
        overlayAdded=false;
    }

    @Override public void onInterrupt() {hideOverlay();}
    @Override public void onDestroy() {
        handler.removeCallbacksAndMessages(null);
        hideOverlay();
        if(prefs!=null) {
            if(listener!=null) prefs.unregisterOnSharedPreferenceChangeListener(listener);
            prefs.edit().putBoolean("service_connected",false).apply();
        }
        super.onDestroy();
    }

    private final class GlowView extends View {
        private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
        private int tint=Color.rgb(42,90,149);
        private float centerX=.50f;
        private ValueAnimator animator;
        GlowView() {
            super(GlowAccessibilityService.this);
            setLayerType(View.LAYER_TYPE_HARDWARE,null);
        }
        void animateTo(int newColor,float absoluteX) {
            centerX=Math.max(.16f,Math.min(.84f,absoluteX/
                (float)Math.max(1,getWidth()>0?getWidth():getResources().getDisplayMetrics().widthPixels)));
            if (tint==newColor) {invalidate();return;}
            if (animator!=null) animator.cancel();
            animator=ValueAnimator.ofArgb(tint,newColor);
            animator.setDuration(180);
            animator.addUpdateListener(a->{tint=(int)a.getAnimatedValue();invalidate();});
            animator.start();
        }
        @Override protected void onDraw(Canvas canvas) {
            int w=getWidth(),h=getHeight();
            if(w<1||h<1)return;
            int level=prefs==null?0:prefs.getInt("intensity",0);
            int strength=level==0?23:level==1?39:57;
            int r=Color.red(tint),g=Color.green(tint),b=Color.blue(tint);
            float radius=(float)Math.hypot(w,h)*.95f;
            paint.setShader(new RadialGradient(w*centerX,h*.48f,radius,
                new int[]{Color.argb(strength,r,g,b),
                          Color.argb(strength*2/3,r,g,b),
                          Color.argb(strength/4,r,g,b),Color.TRANSPARENT},
                new float[]{0f,.38f,.73f,1f},Shader.TileMode.CLAMP));
            canvas.drawRect(0,0,w,h,paint);
            paint.setShader(null);
        }
    }
}
