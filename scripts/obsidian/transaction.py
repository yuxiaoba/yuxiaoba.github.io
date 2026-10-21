"""Git fast-forward and release operations. Never reset, stash, or merge user work."""
import contextlib,fcntl,hashlib,json,os,shutil,subprocess,tarfile,tempfile,time,uuid
from pathlib import Path
from .exporter import ExportError,MANIFEST,plan_changes

@contextlib.contextmanager
def locked(root):
 path=root/'.preview/build.lock';path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('a') as handle:
  try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ExportError('Another build/sync is already running')
  yield

def git(repo,*args):
 return subprocess.check_output(['git','-C',str(repo),*args],text=True,stderr=subprocess.PIPE).strip()

def pull(repo,branch='main',update=True):
 if not (repo/'.git').exists():raise ExportError('Source must be a dedicated Git checkout')
 if git(repo,'status','--porcelain'):raise ExportError('Dedicated source checkout has local changes; refusing pull')
 if git(repo,'branch','--show-current')!=branch:raise ExportError('Source branch differs from configured branch')
 if update:
  subprocess.run(['git','-C',str(repo),'fetch','origin',branch],env={**os.environ,'GIT_TERMINAL_PROMPT':'0','GIT_SSH_COMMAND':'ssh -o BatchMode=yes -o ConnectTimeout=20'},check=True,timeout=180)
  target=git(repo,'rev-parse','FETCH_HEAD')
  if subprocess.run(['git','-C',str(repo),'merge-base','--is-ancestor','HEAD',target],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
   raise ExportError('Remote history diverged; refusing automatic merge/rebase/reset')
  subprocess.run(['git','-C',str(repo),'merge','--ff-only',target],check=True,timeout=60)
 return git(repo,'rev-parse','HEAD')

def source_snapshot(repo,commit,destination):
 destination.mkdir()
 with tempfile.TemporaryFile() as stream:
  subprocess.run(['git','-C',str(repo),'archive',commit],stdout=stream,check=True)
  stream.seek(0)
  with tarfile.open(fileobj=stream) as archive:archive.extractall(destination,filter='data')

EXCLUDE={'.git','.preview','.handoff','.sync-state','.bundle','.sass-cache','node_modules','vendor','_site','__pycache__','docs','tests'}
def fingerprint(root):
 result=hashlib.sha256()
 for base,dirs,files in os.walk(root):
  dirs[:]=sorted(d for d in dirs if d not in EXCLUDE and not d.startswith('.'))
  for name in sorted(files):
   if name.startswith('.') or name.endswith('.pyc'):continue
   path=Path(base)/name
   if path.is_symlink():raise ExportError('Website source symlinks need explicit handling')
   result.update(str(path.relative_to(root)).encode());result.update(hashlib.sha256(path.read_bytes()).digest())
 return result.hexdigest()

def atomic_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
 temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');os.replace(temp,path)

def activate(root,release):
 release=release.resolve();releases=(root/'.preview/releases').resolve()
 if release.parent!=releases or not (release/'pagefind/status.json').exists():raise ExportError('Only complete built releases can be activated')
 link=root/'.preview/current';temporary=root/'.preview'/('current-'+uuid.uuid4().hex)
 temporary.symlink_to(release,target_is_directory=True);os.replace(temporary,link)

def commit_release(root,candidate,files,source_hashes,report,expected_fingerprint):
 if fingerprint(root)!=expected_fingerprint:raise ExportError('Website changed during build; retry with a fresh snapshot')
 old,new,changes=plan_changes(root,files)
 new['sources']=source_hashes
 touched=set(changes['write']+changes['remove']+[MANIFEST])
 backups={name:(root/name).read_bytes() if (root/name).exists() else None for name in touched}
 release=root/'.preview/releases'/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]);release.parent.mkdir(parents=True,exist_ok=True)
 shutil.move(str(candidate),release)
 try:
  for name in changes['write']:
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name('.'+p.name+'.sync-tmp');tmp.write_bytes(files[name]);os.replace(tmp,p)
  for name in changes['remove']:(root/name).unlink()
  if old!=new:atomic_json(root/MANIFEST,new)
  atomic_json(root/'.preview/release-meta'/f'{release.name}.json',report)
  activate(root,release)
 except Exception:
  for name,raw in backups.items():
   p=root/name
   if raw is None:p.unlink(missing_ok=True)
   else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  raise
 return {'release':str(release),'changes':changes}
