"""Distribution only: reconstruct approved signed APKs, verify, then advance public device updates."""
import base64,hashlib,json,os,re,subprocess,tempfile,zipfile,urllib.request,time
from pathlib import Path
REPO='lIlIllIIlIlIIlIIllI/Lycoris-updates'
TAG='v1.4.1'
CERT='62823547a1b9e6e42619f336e5d4a7dfe408a6de81045773a72b087305cebba5'
ROOT=Path('stage11-stable')
def cmd(*a):return subprocess.check_output(a,text=True).strip()
def api(path):return json.loads(cmd('gh','api','repos/'+REPO+'/'+path))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert os.environ['GITHUB_REPOSITORY']==REPO and os.environ['GITHUB_REF']=='refs/heads/stage11-stable-delivery'
 manifest=json.loads((ROOT/'delivery.json').read_text())
 assert manifest['gguf_default'] and manifest['version_code']==51 and len(manifest['source_commit'])==40 and manifest['source_ci']['conclusion']=='success' and manifest['litert_default']=='off'
 assert manifest['tests']=={'tests':765,'failures':0,'errors':0,'skipped':0}
 oldmain=api('git/ref/heads/main')['object']['sha']
 previous={r['id']:[(a['id'],a['name'],a['size'],a.get('digest')) for a in r['assets']] for r in api('releases?per_page=100') if r['tag_name']!=TAG}
 out=Path(tempfile.mkdtemp(prefix='stage11-approved-'));files=[]
 sdk=Path(os.environ['ANDROID_HOME'])
 tools=next(p for p in sorted((sdk/'build-tools').glob('*'),reverse=True) if (p/'apksigner').is_file() and (p/'aapt').is_file())
 for entry in manifest['assets']:
  name=entry['name'];assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]+',name)
  path=out/name
  with path.open('wb') as output:
   for part in entry['parts']:
    assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]+',part)
    with (ROOT/part).open('rb') as source:
     while chunk:=source.read(1024*1024):output.write(chunk)
  assert path.stat().st_size==entry['bytes'] and sha(path)==entry['sha256']
  if name.endswith('.apk'):
   assert CERT in cmd(str(tools/'apksigner'),'verify','--print-certs',str(path))
   badging=cmd(str(tools/'aapt'),'dump','badging',str(path))
   for value in ["name='com.lilac.anime.enhanced'","versionCode='51'","versionName='1.4.1'"]:assert value in badging
   assert 'application-debuggable' not in badging
   subprocess.run([str(tools/'zipalign'),'-c','-P','16','4',str(path)],check=True,capture_output=True)
   with zipfile.ZipFile(path) as archive:
    assert archive.testzip() is None
    natives=[n for n in archive.namelist() if n.startswith('lib/') and n.endswith('.so')]
    assert entry['sdk'] and len(natives)==19
    assert {n:hashlib.sha256(archive.read(n)).hexdigest() for n in natives}==manifest['native_sha256']
    assert not any('Qnn' in n or n.endswith(('.gguf','.litertlm','.jks','.keystore')) for n in archive.namelist())
    dex=b''.join(archive.read(n) for n in archive.namelist() if n.endswith('.dex'))
    assert (b'Lcom/lilac/anime/data/subtitle/translation/experimental/LiteRtTranslationProvider;' in dex)==entry['sdk']
  files.append(path)
 assert len([p for p in files if p.suffix=='.apk'])==1
 update=json.loads((ROOT/'update.json').read_text())
 assert update['versionCode']==51 and update['certificateSha256']==CERT and update['tag']==TAG
 selected=next(e for e in manifest['assets'] if e['name']==update['apk']['url'].rsplit('/',1)[-1])
 assert selected['sdk'] and selected['sha256']==update['apk']['sha256'] and selected['bytes']==update['apk']['bytes']
 releases=[r for r in api('releases?per_page=100') if r['tag_name']==TAG]
 if not releases:
  subprocess.run(['gh','release','create',TAG,'--repo',REPO,'--target',os.environ['GITHUB_SHA'],'--draft','--latest=false','--title','Lycoris 1.4.1 · 통합 Enhanced','--notes-file',str(ROOT/'RELEASE_NOTES.md')],check=True)
  releases=[r for r in api('releases?per_page=100') if r['tag_name']==TAG]
 assert len(releases)==1
 release=api('releases/'+str(releases[0]['id']));assert not release['prerelease']
 for path in files:
  old=next((a for a in release['assets'] if a['name']==path.name),None)
  if old:assert old['size']==path.stat().st_size and old['digest']=='sha256:'+sha(path)
  else:
   assert release['draft'],'Never change already published release assets'
   subprocess.run(['gh','release','upload',TAG,str(path),'--repo',REPO],check=True)
 release=api('releases/'+str(release['id']))
 for path in files:
  asset=next(a for a in release['assets'] if a['name']==path.name)
  assert asset['state']=='uploaded' and asset['size']==path.stat().st_size and asset['digest']=='sha256:'+sha(path)
 if release['draft']:subprocess.run(['gh','release','edit',TAG,'--repo',REPO,'--draft=false','--prerelease=false','--latest=true'],check=True)
 assert not api('releases/'+str(release['id']))['draft']
 # Anonymous public URL must serve the exact signed artifact before device metadata advances.
 verified_download=False
 for attempt in range(3):
  try:
   digest=hashlib.sha256();received=0
   request=urllib.request.Request(update['apk']['url'],headers={'User-Agent':'Lycoris-Updater','Cache-Control':'no-cache'})
   with urllib.request.urlopen(request,timeout=60) as response:
    assert response.status==200
    while chunk:=response.read(1024*1024):digest.update(chunk);received+=len(chunk)
   assert received==selected['bytes'] and digest.hexdigest()==selected['sha256']
   verified_download=True;break
  except Exception:
   if attempt==2:raise
   time.sleep(5)
 assert verified_download
 print('Anonymous published APK SHA256 verified before updater promotion.')
 # Explicit user instruction: publish this validated version for in-app device updates, after assets exist.
 current=api('contents/update.json?ref=main');old=json.loads(base64.b64decode(current['content']))
 if old['versionCode']==51:assert old==update,'Never replace a different payload for the same version'
 else:
  assert old['versionCode']<51 and api('git/ref/heads/main')['object']['sha']==oldmain
  payload={'message':'chore: publish Stage 11 validated device update metadata','branch':'main','sha':current['sha'],'content':base64.b64encode((ROOT/'update.json').read_bytes()).decode()}
  request=out/'request.json';request.write_text(json.dumps(payload))
  subprocess.run(['gh','api','--method','PUT','repos/'+REPO+'/contents/update.json','--input',str(request),'--silent'],check=True)
 assert json.loads(base64.b64decode(api('contents/update.json?ref=main')['content']))==update
 current_readme=api('contents/README.md?ref=main')
 desired=Path('README.md').read_bytes()
 if base64.b64decode(current_readme['content'])!=desired:
  request=out/'readme-request.json'
  request.write_text(json.dumps({'message':'docs: describe unified stable device update','branch':'main','sha':current_readme['sha'],'content':base64.b64encode(desired).decode()}))
  subprocess.run(['gh','api','--method','PUT','repos/'+REPO+'/contents/README.md','--input',str(request),'--silent'],check=True)
 for ident,expected in previous.items():
  r=api('releases/'+str(ident));assert [(a['id'],a['name'],a['size'],a.get('digest')) for a in r['assets']]==expected
 print('Published one stable unified APK; original releases unchanged; public update.json verified; GGUF default and LiteRT opt-in OFF.')
if __name__=='__main__':main()
