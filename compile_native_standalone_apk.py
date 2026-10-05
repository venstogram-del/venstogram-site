import subprocess
import zipfile
import shutil
import os

# Paths to JDK and Android SDK tools
jdk_dir = r'C:\Users\Admin\Music\образование\cardio-ai\tmp_build_tools\jdk'
jdk_bin = os.path.join(jdk_dir, 'bin')
sdk_dir = r'C:\Users\Admin\Music\образование\cardio-ai\tmp_build_tools\sdk'
build_tools = os.path.join(sdk_dir, 'build-tools', '34.0.0')
android_jar = os.path.join(sdk_dir, 'platforms', 'android-34', 'android.jar')

javac_exe = os.path.join(jdk_bin, 'javac.exe')
d8_bat = os.path.join(build_tools, 'd8.bat')
aapt2_exe = os.path.join(build_tools, 'aapt2.exe')
zipalign_exe = os.path.join(build_tools, 'zipalign.exe')
apksigner_bat = os.path.join(build_tools, 'apksigner.bat')
keystore = r'C:\Users\Admin\.android\debug.keystore'

project_dir = r'c:\Users\Admin\Music\образование\STELLOGRAM'
build_dir = os.path.join(project_dir, 'build_tmp')

# Setup environment
env = os.environ.copy()
env['JAVA_HOME'] = jdk_dir
env['PATH'] = f"{jdk_bin};{build_tools};{env.get('PATH', '')}"

print("1. Preparing build directories...")
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)
os.makedirs(build_dir)

src_dir = os.path.join(build_dir, 'src', 'com', 'venstogram', 'app')
os.makedirs(src_dir)

# 2. Write Java MainActivity
java_code = """package com.venstogram.app;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.PermissionRequest;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setMediaPlaybackRequiresUserGesture(false);

        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        request.grant(request.getResources());
                    }
                });
            }
        });

        // Load local application files directly from asset folder
        webView.loadUrl("file:///android_asset/index.html");
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
"""

java_file = os.path.join(src_dir, 'MainActivity.java')
with open(java_file, 'w', encoding='utf-8') as f:
    f.write(java_code)

print("2. Compiling Java code to .class...")
classes_dir = os.path.join(build_dir, 'classes')
os.makedirs(classes_dir)

cmd_javac = [javac_exe, '-cp', android_jar, '-d', classes_dir, java_file]
subprocess.run(cmd_javac, check=True, env=env)

print("3. Converting .class to DEX (classes.dex) with d8...")
cmd_d8 = [d8_bat, '--lib', android_jar, '--output', build_dir, os.path.join(classes_dir, 'com', 'venstogram', 'app', 'MainActivity.class'), os.path.join(classes_dir, 'com', 'venstogram', 'app', 'MainActivity$1.class'), os.path.join(classes_dir, 'com', 'venstogram', 'app', 'MainActivity$1$1.class')]
subprocess.run(cmd_d8, check=True, env=env)

print("4. Compiling Android Resources with AAPT2...")
manifest_file = os.path.join(project_dir, 'android_project', 'AndroidManifest.xml')
compiled_res_dir = os.path.join(build_dir, 'compiled_res')
os.makedirs(compiled_res_dir)

res_dir = os.path.join(build_dir, 'res')
values_dir = os.path.join(res_dir, 'values')
os.makedirs(values_dir)
with open(os.path.join(values_dir, 'strings.xml'), 'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?><resources><string name="app_name">Venstogram</string></resources>')

# Link resources
unsigned_apk = os.path.join(build_dir, 'unsigned.apk')
cmd_aapt_link = [
    aapt2_exe, 'link',
    '-I', android_jar,
    '--manifest', manifest_file,
    '-o', unsigned_apk
]
subprocess.run(cmd_aapt_link, check=True, env=env)

print("5. Packaging local web app assets & DEX into APK...")
with zipfile.ZipFile(unsigned_apk, 'a') as apk:
    # Add compiled classes.dex
    dex_file = os.path.join(build_dir, 'classes.dex')
    apk.write(dex_file, 'classes.dex')
    
    # Add web application files into assets/
    web_files = ['index.html', 'style.css', 'app.js', 'manifest.json', 'sw.js']
    for wf in web_files:
        fp = os.path.join(project_dir, wf)
        if os.path.exists(fp):
            apk.write(fp, f'assets/{wf}')
    
    icons_dir = os.path.join(project_dir, 'icons')
    if os.path.exists(icons_dir):
        for root, dirs, files in os.walk(icons_dir):
            for file in files:
                fp = os.path.join(root, file)
                rel = os.path.relpath(fp, project_dir)
                apk.write(fp, f'assets/{rel}'.replace('\\', '/'))

print("6. Aligning APK with zipalign...")
aligned_apk = os.path.join(build_dir, 'aligned.apk')
cmd_align = [zipalign_exe, '-f', '-p', '4', unsigned_apk, aligned_apk]
subprocess.run(cmd_align, check=True, env=env)

print("7. Signing APK with apksigner...")
final_apk = os.path.join(project_dir, 'Venstogram.apk')
if os.path.exists(final_apk): os.remove(final_apk)
shutil.copy(aligned_apk, final_apk)

cmd_sign = [
    apksigner_bat, 'sign',
    '--ks', keystore,
    '--ks-pass', 'pass:android',
    '--key-pass', 'pass:android',
    '--ks-key-alias', 'androiddebugkey',
    final_apk
]
subprocess.run(cmd_sign, check=True, env=env)

print("8. Verifying final APK...")
cmd_verify = [apksigner_bat, 'verify', final_apk]
subprocess.run(cmd_verify, check=True, env=env)

# Clean build temp
shutil.rmtree(build_dir)

print("SUCCESS! Standalone native Venstogram.apk built successfully!")
