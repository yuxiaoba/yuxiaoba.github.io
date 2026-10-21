#!/usr/bin/env python3
"""Start an independent tmux preview without stopping any existing service."""
import datetime,json,socket,subprocess,time,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run(['python3','scripts/watch_site.py','--once'],cwd=root,check=True)
for port in range(4000,4100):
    with socket.socket() as sock:
        try:sock.bind(('127.0.0.1',port))
        except OSError:continue
        break
else:raise SystemExit('No free preview port in 4000–4099')
session='homepage-preview'
if subprocess.run(['tmux','has-session','-t',session],capture_output=True).returncode==0:
    session+='-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
subprocess.run(['tmux','new-session','-d','-s',session,'-n','jekyll','-c',str(root),'bash','scripts/preview.sh',str(port)],check=True)
subprocess.run(['tmux','new-window','-t',session,'-n','build','-c',str(root),'bash','scripts/watch_preview.sh'],check=True)
url=f'http://127.0.0.1:{port}'
for _ in range(40):
    try:
        with urllib.request.urlopen(url+'/zh/',timeout=2) as response:
            if response.status==200:break
    except (OSError,urllib.error.URLError):time.sleep(.5)
else:raise SystemExit(f'Preview did not become ready. Inspect tmux {session}:jekyll and .preview/jekyll.log')
state={'url':url,'port':port,'session':session,'window':'jekyll','log':str(root/'.preview/jekyll.log'),'started':datetime.datetime.now().isoformat()}
(root/'.preview/preview.json').write_text(json.dumps(state,indent=2))
print(json.dumps(state,indent=2))
