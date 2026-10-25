"""Verify uploaded tester files before making the prerelease visible."""
import argparse,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO='CloudyCodez/FF-O'
TAG='v0.1.0'

def release():
    return json.loads(subprocess.check_output(['gh','release','view',TAG,'--repo',REPO,'--json','assets,isDraft']))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--wait-upload',action='store_true');args=parser.parse_args()
    files=[ROOT/'dist'/name for name in ('FFO-Hub.apk','FFO-Client.apk','FFO-Download.json')]+sorted((ROOT/'dist/data').glob('FFO-Data.part*'))
    assert len(files)==11,'Expected both APKs, manifest and eight parts'
    deadline=time.monotonic()+3*3600
    while True:
        assets={a['name']:a for a in release()['assets']}
        missing=[p.name for p in files if p.name not in assets or assets[p.name]['state']!='uploaded' or assets[p.name]['size']!=p.stat().st_size]
        if not missing:break
        if not args.wait_upload or time.monotonic()>deadline:raise RuntimeError('Incomplete release: '+', '.join(missing))
        print('Awaiting upload: '+', '.join(missing),flush=True);time.sleep(45)
    subprocess.run(['gh','release','edit',TAG,'--repo',REPO,'--draft=false','--prerelease'],check=True)
    print('Published https://github.com/'+REPO+'/releases/tag/'+TAG,flush=True)

if __name__=='__main__':main()
