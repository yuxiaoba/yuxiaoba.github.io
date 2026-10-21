#!/usr/bin/env python3
"""Read-only availability check. A blocked remote host is reported, not rewritten."""
import concurrent.futures,json,urllib.request,urllib.error,sys
from pathlib import Path
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[1]
doc=BeautifulSoup((root/'.preview/current/publications/index.html').read_text(),'html.parser')
urls=json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv)>1 else sorted({a['href'] for a in doc.select('.publication-links a') if a['href'].startswith(('http://','https://'))})
def probe(url):
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (homepage link validation)'},method='HEAD')
        with urllib.request.urlopen(request,timeout=15) as response:return {'url':url,'status':response.status,'final_url':response.url}
    except urllib.error.HTTPError as error:return {'url':url,'status':error.code,'error':str(error)}
    except Exception as error:return {'url':url,'status':None,'error':str(error)}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:results=list(pool.map(probe,urls))
report={'checked':len(results),'ok':sum(r['status'] is not None and r['status']<400 for r in results),'results':results}
(root/'.preview'/(sys.argv[2] if len(sys.argv)>2 else 'external-links.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='results'}))
for row in results:
    if row['status'] is None or row['status']>=400:print(json.dumps(row))
