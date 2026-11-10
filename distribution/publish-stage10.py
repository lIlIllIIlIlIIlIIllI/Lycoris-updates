"""Distribution only: reconstruct approved signed APKs, verify, then advance public device updates."""
import base64,hashlib,json,os,re,subprocess,tempfile,zipfile
from pathlib import Path
REPO='lIlIllIIlIlIIlIIllI/Lycoris-updates'
TAG='v3-ai-stage10-preview.10'
CERT='62823547a1b9e6e42619f336e5d4a7dfe408a6de81045773a72b087305cebba5'
ROOT=Path('stage10-preview')
def cmd(*a):return subprocess.check_output(a,text=True).strip()
def api(path):return json.loads(cmd('gh','api','repos/'+REPO+'/'+path))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert os.environ['GITHUB_REPOSITORY']==REPO and os.environ['GITHUB_REF']=='refs/heads/stage10-preview-delivery'
 manifest=json.loads((ROOT/'delivery.json').read_text())
 assert manifest['gguf_default'] and manifest['version_code']==50 and manifest['source_commit']=='dcd67f844cf65185e0d1bb5932395b39fc2a5601'
 assert manifest['tests']=={'tests':744,'failures':0,'errors':0,'skipped':0}
 oldmain=api('git/ref/heads/main')['object']['sha']
 previous={r['id']:[(a['id'],a['name'],a['size'],a.get('digest')) for a in r['assets']] for r in api('releases?per_page=100') if r['tag_name']!=TAG}
 out=Path(tempfile.mkdtemp(prefix='stage10-approved-'));files=[]
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
   for value in ["name='com.lilac.anime.enhanced'","versionCode='50'","versionName='1.4.1-preview.10'"]:assert value in badging
   assert 'application-debuggable' not in badging
   subprocess.run([str(tools/'zipalign'),'-c','-P','16','4',str(path)],check=True,capture_output=True)
   with zipfile.ZipFile(path) as archive:
    assert archive.testzip() is None
    natives=[n for n in archive.namelist() if n.startswith('lib/') and n.endswith('.so')]
    assert len(natives)==(19 if entry['sdk'] else 18)
    dex=b''.join(archive.read(n) for n in archive.namelist() if n.endswith('.dex'))
    assert (b'Lcom/lilac/anime/data/subtitle/translation/experimental/LiteRtTranslationProvider;' in dex)==entry['sdk']
  files.append(path)
 update=json.loads((ROOT/'update.json').read_text())
 assert update['versionCode']==50 and update['certificateSha256']==CERT and update['tag']==TAG
 selected=next(e for e in manifest['assets'] if e['name']==update['apk']['url'].rsplit('/',1)[-1])
 assert selected['sdk'] and selected['sha256']==update['apk']['sha256'] and selected['bytes']==update['apk']['bytes']
 releases=[r for r in api('releases?per_page=100') if r['tag_name']==TAG]
 if not releases:
  subprocess.run(['gh','release','create',TAG,'--repo',REPO,'--target',oldmain,'--draft','--prerelease','--latest=false','--title','Lycoris 1.4.1-preview.10 · Stage 10 선택형 AI 엔진','--notes-file',str(ROOT/'RELEASE_NOTES.md')],check=True)
  releases=[r for r in api('releases?per_page=100') if r['tag_name']==TAG]
 assert len(releases)==1
 release=api('releases/'+str(releases[0]['id']));assert release['prerelease']
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
 if release['draft']:subprocess.run(['gh','release','edit',TAG,'--repo',REPO,'--draft=false','--prerelease','--latest=false'],check=True)
 assert not api('releases/'+str(release['id']))['draft']
 # Explicit user instruction: publish this validated version for in-app device updates, after assets exist.
 current=api('contents/update.json?ref=main');old=json.loads(base64.b64decode(current['content']))
 if old['versionCode']==50:assert old==update,'Never replace a different payload for the same version'
 else:
  assert old['versionCode']<50 and api('git/ref/heads/main')['object']['sha']==oldmain
  payload={'message':'chore: publish Stage 10 validated device update metadata','branch':'main','sha':current['sha'],'content':base64.b64encode((ROOT/'update.json').read_bytes()).decode()}
  request=out/'request.json';request.write_text(json.dumps(payload))
  subprocess.run(['gh','api','--method','PUT','repos/'+REPO+'/contents/update.json','--input',str(request),'--silent'],check=True)
 assert json.loads(base64.b64decode(api('contents/update.json?ref=main')['content']))==update
 for ident,expected in previous.items():
  r=api('releases/'+str(ident));assert [(a['id'],a['name'],a['size'],a.get('digest')) for a in r['assets']]==expected
 print('Published new preview, original releases unchanged; update.json points to the verified signed AI APK with GGUF default.')
if __name__=='__main__':main()
