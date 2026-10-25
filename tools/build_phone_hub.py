"""Bundle the current gateway and required master data, then build Android Hub."""
import json, os, shutil, subprocess, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HUB=ROOT/'AndroidHub'
GRADLE=Path.home()/'.gradle/wrapper/dists/gradle-8.14.3-bin/cv11ve7ro1n3o1j4so8xd9n66/gradle-8.14.3/bin/gradle.bat'

def main():
    dest=HUB/'app/src/main/assets/runtime.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as archive:
        for base in ('server','assets/decoded/mst','assets/client-compat'):
            for file in (ROOT/base).rglob('*'):
                if file.is_file() and '__pycache__' not in file.parts and not file.name.startswith('test'):
                    archive.write(file,file.relative_to(ROOT).as_posix())
        for name in ('native-requests.json','local-version-catalog.json','local-text-catalog.json','registry-master-catalog.json','community/missions.json'):
            archive.write(ROOT/'research'/name,'research/'+name)
    env=os.environ.copy();env['JAVA_HOME']='C:/Program Files/Android/openjdk/jdk-21.0.8'
    subprocess.run([str(GRADLE),'-p',str(HUB),':app:assembleDebug','--console=plain','--no-daemon'],env=env,check=True)
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    shutil.copy2(HUB/'app/build/outputs/apk/debug/app-debug.apk',dist/'FFO-Hub.apk')
    cache=ROOT/'assets/cache'
    files=[{'path':p.relative_to(cache).as_posix(),'bytes':p.stat().st_size} for p in cache.rglob('*') if p.is_file()]
    (dist/'FFO-Data-Manifest.json').write_text(json.dumps({'files':files,'bytes':sum(row['bytes'] for row in files)},separators=(',',':')),encoding='utf-8')
    print('Built',dist/'FFO-Hub.apk')

if __name__=='__main__':main()
