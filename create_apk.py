import zipfile
import os

apk_path = os.path.join(os.getcwd(), 'Venstogram.apk')

manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.venstogram.app"
    android:versionCode="1"
    android:versionName="1.0.0">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <application
        android:label="Venstogram"
        android:icon="@mipmap/ic_launcher"
        android:theme="@android:style/Theme.NoTitleBar"
        android:hardwareAccelerated="true">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>"""

with zipfile.ZipFile(apk_path, 'w', zipfile.ZIP_DEFLATED) as apk:
    # 1. Android Manifest
    apk.writestr('AndroidManifest.xml', manifest_content)
    
    # 2. Add all web application files to assets/www/
    base_dir = os.getcwd()
    for root, dirs, files in os.walk(base_dir):
        if 'android_project' in root or '.git' in root or 'icons' in root and 'icons' not in root.split(os.sep)[-1]:
            continue
        for file in files:
            if file.endswith('.apk') or file.endswith('.pyc') or file == 'create_apk.py':
                continue
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, base_dir)
            arcname = os.path.join('assets/www', rel_path).replace('\\', '/')
            apk.write(file_path, arcname)

print(f"APK file created successfully: {apk_path}")
