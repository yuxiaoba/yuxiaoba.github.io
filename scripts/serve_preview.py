#!/usr/bin/env python3
"""Serve only completed static output with explicit cache revalidation."""
import argparse,functools
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
class Handler(SimpleHTTPRequestHandler):
 def end_headers(self):
  self.send_header('Cache-Control','no-cache');super().end_headers()
 def list_directory(self,path):self.send_error(404);return None
p=argparse.ArgumentParser();p.add_argument('--bind',default='127.0.0.1');p.add_argument('--port',type=int,required=True);p.add_argument('--directory',type=Path,required=True);a=p.parse_args()
if not (a.directory/'index.html').exists():raise SystemExit('No complete site at preview directory')
# Keep this path unresolved: new requests must follow the active release symlink.
server=ThreadingHTTPServer((a.bind,a.port),functools.partial(Handler,directory=str(a.directory.absolute())))
print(f'Serving {a.directory} on {a.bind}:{a.port}',flush=True);server.serve_forever()
