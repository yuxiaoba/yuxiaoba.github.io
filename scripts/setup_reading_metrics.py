"""Create private credentials once; never print passwords or overwrite existing keys."""
import argparse
import hashlib
import json
import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(); p.add_argument('--port', type=int, default=443); args=p.parse_args()
private=ROOT/'.metrics';private.mkdir(mode=0o700,exist_ok=True);os.chmod(private,0o700)
settings=private/'settings.json';access=private/'admin-access.json'
if settings.exists() or access.exists():
    if not settings.exists() or not access.exists(): raise SystemExit('Incomplete credentials; inspect without replacing existing files')
    print('Existing private credentials preserved')
else:
    password=secrets.token_urlsafe(32)
    suffix='' if args.port==443 else ':'+str(args.port)
    config={'directory':'/var/lib/homepage-reading-metrics/validation','secret':secrets.token_hex(32),
            'catalog':str(ROOT/'.preview/current/reading-metrics.json'),'username':'owner',
            'password_sha256':hashlib.sha256(password.encode()).hexdigest()}
    for path,value in [(settings,config),(access,{'url':'https://111.119.236.134'+suffix+'/admin','username':'owner','password':password})]:
        with open(path,'x',opener=lambda path,flags:os.open(path,flags,0o600)) as stream: json.dump(value,stream,indent=2)
    print('Private credentials created; initial counts use isolated validation storage')
print('Owner login information:',access)
