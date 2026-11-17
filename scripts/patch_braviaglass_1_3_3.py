#!/usr/bin/env python3
"""BraviaGlass 1.3.3 — Android 9 PackageManager archive-signature compatibility.

Run *after* scripts/patch_braviaglass_1_3_2.py on the unpacked public source.
A missing archive signingInfo triggers full JAR-v1 verification against the
currently installed application's certificate. Differing reported signers
still fail closed. Android PackageInstaller performs its own signature checks.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
manager = root / "app/src/main/java/com/usman/braviaglass/UpdateManager.java"
gradle = root / "app/build.gradle"
source = manager.read_text(encoding="utf-8")
source_orig=source
source=source.replace(
    'import java.util.Arrays;\n',
    'import java.util.Arrays;\n'
    'import java.util.Enumeration;\n'
    'import java.util.jar.JarEntry;\n'
    'import java.util.jar.JarFile;\n'
)
source=source.replace(
    '        final int flag=Build.VERSION.SDK_INT>=28?PackageManager.GET_SIGNING_CERTIFICATES:PackageManager.GET_SIGNATURES;',
    '        // Android 9 may omit archive.signingInfo for getPackageArchiveInfo.\n'
    '        // Ask for both forms; fall back only when the archive signer is absent.\n'
    '        final int flag=Build.VERSION.SDK_INT>=28\n'
    '            ?PackageManager.GET_SIGNING_CERTIFICATES|PackageManager.GET_SIGNATURES\n'
    '            :PackageManager.GET_SIGNATURES;'
)
source=source.replace(
    '        if(a==null||b==null||a.length!=1||b.length!=1||!Arrays.equals(a[0].toByteArray(),b[0].toByteArray()))\n'
    '            throw new SecurityException("Подпись APK не совпадает с установленным BraviaGlass");',
    '        if(b==null||b.length!=1)\n'
    '            throw new SecurityException("Не удалось проверить подпись установленного BraviaGlass");\n'
    '        if(a==null||a.length==0) {\n'
    '            // Older Sony Android 9 reports null archive signatures even for\n'
    '            // a valid signed APK. Fully verify the APK v1/JAR signatures.\n'
    '            verifyV1ArchiveSignatures(apk,b[0]);\n'
    '        } else if(a.length!=1 || !Arrays.equals(a[0].toByteArray(),b[0].toByteArray())) {\n'
    '            // A known different archive certificate is never accepted.\n'
    '            throw new SecurityException("Подпись APK не совпадает с установленным BraviaGlass");\n'
    '        }'
)
source=source.replace(
    '        if(Build.VERSION.SDK_INT>=28)return pkg.signingInfo==null?null:pkg.signingInfo.getApkContentsSigners();\n'
    '        return pkg.signatures;',
    '        if(Build.VERSION.SDK_INT>=28 && pkg.signingInfo!=null) {\n'
    '            Signature[] result=pkg.signingInfo.getApkContentsSigners();\n'
    '            if(result!=null && result.length>0)return result;\n'
    '        }\n'
    '        return pkg.signatures;'
)
needle='    static boolean canInstall(Context context)'
new='''    /**
     * Safe compatibility fallback for Sony Android 9's archive PackageInfo.
     * Verifies every non-META-INF entry of the APK with the Java JAR verifier,
     * and requires the exact X.509 certificate of the installed launcher.
     * Invalid, unsigned, or mixed-signer APK content is rejected.
     * The Android package installer will additionally enforce the APK v2 signature.
     */
    private static void verifyV1ArchiveSignatures(File apk,Signature installedSigner) throws Exception {
        try(JarFile jar=new JarFile(apk,true)) {
            Enumeration<JarEntry> entries=jar.entries();
            final byte[] expected=installedSigner.toByteArray();
            final byte[] buf=new byte[32768];
            int verified=0;
            while(entries.hasMoreElements()) {
                JarEntry entry=entries.nextElement();
                if(entry.isDirectory() || entry.getName().toUpperCase(Locale.ROOT).startsWith("META-INF/"))continue;
                try(InputStream in=jar.getInputStream(entry)) {
                    while(in.read(buf)!=-1) { /* Force full JarVerifier check. */ }
                }
                java.security.cert.Certificate[] certs=entry.getCertificates();
                if(certs==null || certs.length==0)
                    throw new SecurityException("В APK есть неподписанный файл: "+entry.getName());
                boolean trusted=false;
                for(java.security.cert.Certificate cert:certs) {
                    if(Arrays.equals(cert.getEncoded(),expected))trusted=true;
                }
                if(!trusted)
                    throw new SecurityException("Подпись APK не совпадает с установленным BraviaGlass");
                verified++;
            }
            if(verified<2)throw new SecurityException("Не удалось проверить целостность APK");
        }
    }

'''
source=source.replace(needle,new+needle)
if source==source_orig or source.count("verifyV1ArchiveSignatures(apk,b[0]);")!=1 or source.count("private static void verifyV1ArchiveSignatures(")!=1 or source.count("import java.util.Enumeration;")!=1:
    raise SystemExit("UpdateManager compatibility patch failed; refusing to build")
manager.write_text(source,encoding="utf-8")
gr=gradle.read_text(encoding="utf-8")
if gr.count("versionCode 13")!=1 or gr.count("versionName '1.3.2'")!=1:
    raise SystemExit("Unexpected source version")
gradle.write_text(gr.replace("versionCode 13","versionCode 14").replace("versionName '1.3.2'","versionName '1.3.3'"),encoding="utf-8")
print("BraviaGlass 1.3.3: Android 9 archive-signing fallback patched; old-data migration not required.")
