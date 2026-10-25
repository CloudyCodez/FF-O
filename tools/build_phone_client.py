"""Build the ARM64 phone client with persistent local routing, without root."""
import hashlib,json,lzma,subprocess
from pathlib import Path
import frida_tools
ROOT=Path(__file__).resolve().parents[1]
JAVA=Path('C:/Program Files/Android/openjdk/jdk-21.0.8/bin/java.exe')
SDK=Path('C:/Program Files (x86)/Android/android-sdk/build-tools/36.0.0')

def run(*args):subprocess.run(list(map(str,args)),cwd=ROOT,check=True)

def main():
    merged=ROOT/'research/phone-merged.apk'
    if not merged.exists():run(JAVA,'-jar','E:/BlackClover-Offline/Tools/APKEditor.jar','merge','-i',ROOT/'client/original','-o',merged,'-extractNativeLibs','true','-clean-meta')
    decoded=ROOT/'research/phone-client'
    if not decoded.exists():run(JAVA,'-jar',ROOT/'tools/android/apktool.jar','d',merged,'-o',decoded)
    lib=decoded/'lib/arm64-v8a'
    (lib/'libfforoute.so').write_bytes(lzma.decompress((ROOT/'tools/android/gadget.so.xz').read_bytes()))
    (lib/'libfforoute.config.so').write_text(json.dumps({'interaction':{'type':'script','path':'libfforoute.js.so','on_change':'ignore'},'runtime':'v8','teardown':'minimal'}),encoding='utf-8')
    bridge=(Path(frida_tools.__file__).parent/'bridges/java.js').read_text(encoding='utf-8')
    script=bridge+'\n'+(ROOT/'tools/route_client.js').read_text(encoding='utf-8')+'\n'+(ROOT/'tools/route_native_assets.js').read_text(encoding='utf-8')
    (lib/'libfforoute.js.so').write_text(script,encoding='utf-8')
    smali=decoded/'smali/com/square_enix/android_googleplay/FFBEWW/LapisApplication.smali'
    source=smali.read_text(encoding='utf-8');needle='invoke-super {p0}, Landroid/app/Application;->onCreate()V'
    if 'fforoute' not in source:
        assert needle in source
        source=source.replace(needle,needle+'\n\n    const-string v0, "fforoute"\n    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V')
        smali.write_text(source,encoding='utf-8')
    manifest=decoded/'AndroidManifest.xml';source=manifest.read_text(encoding='utf-8').replace('android:label="FFEXVIUS"','android:label="FF:O"')
    for attr in ('android:usesCleartextTraffic="true"','android:debuggable="true"'):
        if attr not in source:source=source.replace('<application ','<application '+attr+' ',1)
    manifest.write_text(source,encoding='utf-8')
    unsigned=ROOT/'research/phone-unsigned.apk';aligned=ROOT/'research/phone-aligned.apk'
    run(JAVA,'-jar',ROOT/'tools/android/apktool.jar','b',decoded,'-o',unsigned)
    run(SDK/'zipalign.exe','-f','-P','16','4',unsigned,aligned)
    dist=ROOT/'dist';dist.mkdir(exist_ok=True);apk=dist/'FFO-Client.apk'
    run(SDK/'apksigner.bat','sign','--ks',Path.home()/'.android/debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',apk,aligned)
    run(SDK/'apksigner.bat','verify',apk)
    (dist/'FFO-Client.sha256').write_text(hashlib.sha256(apk.read_bytes()).hexdigest()+'  FFO-Client.apk\n')
    print('Built',apk)

if __name__=='__main__':main()
