#!/usr/bin/env python3
"""Verify the live tmux preview, including served PDF bytes and private exclusions."""
import hashlib,json,subprocess,urllib.request,urllib.error
from pathlib import Path
root=Path(__file__).resolve().parents[1]
state=json.loads((root/'.preview/preview.json').read_text());base=state['url'];checks=[]
for route in ['/','/zh/','/publications/','/zh/publications/','/digest/','/zh/digest/','/kitchen/','/zh/kitchen/','/life/','/zh/life/','/publications.html']:
 with urllib.request.urlopen(base+route) as response:
  assert response.status==200
  text=response.read().decode();assert '<html lang=' in text and 'NEVER_OUTPUT' not in text and 'Paired article fixture' not in text
  checks.append(route)
with urllib.request.urlopen(base+'/files/ASPLOS25/Mint.pdf') as response:
 assert hashlib.sha256(response.read()).hexdigest()=='689902a7753a9fa3c9ba031e3be338c6d7e120a1399c4f600c67caf6427f4c03'
checks.append('served Mint matches user PDF')
for route in ['/files/FSE24/changerca.pdf','/.handoff/STATUS.md','/docs/content/README.md','/scripts/verify_site.py','/AGENTS.md','/.preview/fixture-site/index.html','/digest/zh/2026-10-10-paired/']:
 try:urllib.request.urlopen(base+route)
 except urllib.error.HTTPError as error:assert error.code==404
 else:raise AssertionError('Unexpected public output '+route)
 checks.append('excluded '+route)
pane=subprocess.check_output(['tmux','list-panes','-t',state['session']+':'+state['window'],'-F','#{pane_dead} #{pane_current_command}'],text=True).strip()
assert pane.startswith('0 '),pane
listeners=subprocess.check_output(['ss','-ltnp'],text=True)
assert f'127.0.0.1:{state["port"]}' in listeners
assert f'0.0.0.0:{state["port"]}' not in listeners
checks.extend(['tmux pane alive','loopback-only listener'])
(root/'.preview/preview-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'pane':pane},indent=2))
print(json.dumps({'passed':len(checks),'url':base,'pane':pane}))
