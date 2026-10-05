import subprocess
import zipfile
import shutil
import os

base_apk = r'C:\Users\Admin\Music\образование\cardio-ai\medscan-cardio-android\app\build\outputs\apk\debug\app-debug.apk'
output_dir = r'c:\Users\Admin\Music\образование\STELLOGRAM'
temp_apk = os.path.join(output_dir, 'temp_unsigned.apk')
aligned_apk = os.path.join(output_dir, 'temp_aligned.apk')
final_apk = os.path.join(output_dir, 'Venstogram.apk')

jdk_dir = r'C:\Users\Admin\Music\образование\cardio-ai\tmp_build_tools\jdk'
jdk_bin = os.path.join(jdk_dir, 'bin')
zipalign_exe = r'C:\Users\Admin\Music\образование\cardio-ai\tmp_build_tools\sdk\build-tools\34.0.0\zipalign.exe'
apksigner_bat = r'C:\Users\Admin\Music\образование\cardio-ai\tmp_build_tools\sdk\build-tools\34.0.0\apksigner.bat'
keystore = r'C:\Users\Admin\.android\debug.keystore'

# Setup environment with JAVA_HOME and PATH
env = os.environ.copy()
env['JAVA_HOME'] = jdk_dir
env['PATH'] = f"{jdk_bin};{env.get('PATH', '')}"

print("1. Extracting base APK and injecting Venstogram assets...")
shutil.copy(base_apk, temp_apk)

# Inject all Venstogram files into assets/ in the APK
web_files = ['index.html', 'style.css', 'app.js', 'manifest.json', 'sw.js']
icons_dir = os.path.join(output_dir, 'icons')

with zipfile.ZipFile(temp_apk, 'a') as apk:
    for wf in web_files:
        p = os.path.join(output_dir, wf)
        if os.path.exists(p):
            apk.write(p, f'assets/{wf}')
            apk.write(p, f'assets/www/{wf}')
    
    if os.path.exists(icons_dir):
        for root, dirs, files in os.walk(icons_dir):
            for file in files:
                fp = os.path.join(root, file)
                rel = os.path.relpath(fp, output_dir)
                apk.write(fp, f'assets/{rel}'.replace('\\', '/'))
                apk.write(fp, f'assets/www/{rel}'.replace('\\', '/'))

print("2. Running ZipAlign...")
if os.path.exists(aligned_apk): os.remove(aligned_apk)
cmd_align = [zipalign_exe, '-f', '-p', '4', temp_apk, aligned_apk]
subprocess.run(cmd_align, check=True, env=env)

print("3. Signing APK with apksigner...")
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

# Verify APK signature
cmd_verify = [apksigner_bat, 'verify', final_apk]
subprocess.run(cmd_verify, check=True, env=env)

# Clean temp files
if os.path.exists(temp_apk): os.remove(temp_apk)
if os.path.exists(aligned_apk): os.remove(aligned_apk)

print("SUCCESS: Fully signed and verified Venstogram.apk created at:", final_apk)
