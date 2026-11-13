"""Publish a new, verified preview. Never replace old assets, tags or stable Latest."""
import base64,hashlib,json,os,re,subprocess,tempfile,time,urllib.request,zipfile
from pathlib import Path
REPO='lIlIllIIlIlIIlIIllI/Lycoris-updates'
TAG='v1.4.2-preview.3'
ROOT=Path('moeni-preview3')
CERT='62823547a1b9e6e42619f336e5d4a7dfe408a6de81045773a72b087305cebba5'
def cmd(*args):return subprocess.check_output(args,text=True).strip()
def api(path):return json.loads(cmd('gh','api','repos/'+REPO+'/'+path))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mutate(path,method,payload,out):
 request=out/'request.json';request.write_text(json.dumps(payload))
 return json.loads(cmd('gh','api','--method',method,'repos/'+REPO+'/'+path,'--input',str(request)))
def main():
 assert os.environ['GITHUB_REPOSITORY']==REPO and os.environ['GITHUB_REF']=='refs/heads/moeni-preview3-delivery'
 data=json.loads((ROOT/'delivery.json').read_text())
 assert data['version_code']==54 and data['gguf_default'] and data['litert_default']=='off'
 assert data['tests']=={'tests':914,'failures':0,'errors':0,'skipped':0}
 assert data['source_ci']['conclusion']=='success' and data['source_ci']['headSha']==data['source_commit']
 releases=api('releases?per_page=100')
 previous={r['id']:{'tag':r['tag_name'],'assets':[(a['id'],a['name'],a['size'],a.get('digest')) for a in r['assets']]} for r in releases if r['tag_name']!=TAG}
 assert api('releases/latest')['tag_name']=='v1.4.1'
 out=Path(tempfile.mkdtemp(prefix='moeni-fix-verified-'));files=[]
 sdk=Path(os.environ['ANDROID_HOME'])
 tools=next(p for p in sorted((sdk/'build-tools').glob('*'),reverse=True) if (p/'apksigner').is_file() and (p/'aapt').is_file())
 for entry in data['assets']:
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
   for value in ["name='com.lilac.anime.enhanced'","versionCode='54'","versionName='1.4.2-preview.3'"]:assert value in badging
   assert 'application-debuggable' not in badging
   subprocess.run([str(tools/'zipalign'),'-c','-P','16','4',str(path)],check=True,capture_output=True)
   with zipfile.ZipFile(path) as archive:
    assert archive.testzip() is None
    natives=[n for n in archive.namelist() if n.startswith('lib/') and n.endswith('.so')]
    assert len(natives)==19 and {n:hashlib.sha256(archive.read(n)).hexdigest() for n in natives}==data['native_sha256']
    assert not any('Qnn' in n or n.endswith(('.gguf','.litertlm','.jks','.keystore')) for n in archive.namelist())
    dex=b''.join(archive.read(n) for n in archive.namelist() if n.endswith('.dex'))
    for cls in [b'Lcom/lilac/anime/crosssite/CrossSiteIndex;',b'Lcom/lilac/anime/crosssite/CrossSiteStore;',b'Lcom/lilac/anime/data/MoeniClient;',b'Lcom/lilac/anime/data/MoeniResponseCache;',b'Lcom/lilac/anime/ui/detail/MoeniDetailScreenKt;',b'Lcom/lilac/anime/data/subtitle/translation/experimental/LiteRtTranslationProvider;']:assert cls in dex
  files.append(path)
 assert len([p for p in files if p.suffix=='.apk'])==1
 update=json.loads((ROOT/'update.json').read_text())
 assert update['versionCode']==54 and update['certificateSha256']==CERT and update['tag']==TAG
 selected=next(e for e in data['assets'] if e['name']==update['apk']['url'].rsplit('/',1)[-1])
 assert selected['sha256']==update['apk']['sha256'] and selected['bytes']==update['apk']['bytes']
 release=next((r for r in releases if r['tag_name']==TAG),None)
 if release is None:
  # Capture the ID returned by creation. Unpublished tag lookup may return 404.
  release=mutate('releases','POST',{'tag_name':TAG,'target_commitish':os.environ['GITHUB_SHA'],
   'name':'Lycoris 1.4.2-preview.3 · 모에니 콘텐츠 복구','body':(ROOT/'RELEASE_NOTES.md').read_text(),
   'draft':True,'prerelease':True,'make_latest':'false'},out)
 assert release['tag_name']==TAG and release['prerelease'] and release['target_commitish']==os.environ['GITHUB_SHA'],'Refuse an unrelated or modified existing release'
 release_id=release['id'];print('Owned preview draft ID:',release_id,flush=True)
 for path in files:
  existing=next((a for a in release['assets'] if a['name']==path.name),None)
  if existing:assert existing['size']==path.stat().st_size and existing['digest']=='sha256:'+sha(path)
  else:
   assert release['draft'],'Never modify published release assets'
   subprocess.run(['gh','release','upload',TAG,str(path),'--repo',REPO],check=True)
 release=api('releases/'+str(release_id))
 for path in files:
  asset=next(a for a in release['assets'] if a['name']==path.name)
  assert asset['state']=='uploaded' and asset['size']==path.stat().st_size and asset['digest']=='sha256:'+sha(path)
 if release['draft']:mutate('releases/'+str(release_id),'PATCH',{'draft':False,'prerelease':True,'make_latest':'false'},out)
 assert not api('releases/'+str(release_id))['draft']
 for attempt in range(3):
  try:
   digest=hashlib.sha256();received=0
   request=urllib.request.Request(update['apk']['url'],headers={'User-Agent':'Lycoris-Updater','Cache-Control':'no-cache'})
   with urllib.request.urlopen(request,timeout=60) as response:
    assert response.status==200
    while chunk:=response.read(1024*1024):digest.update(chunk);received+=len(chunk)
   assert received==selected['bytes'] and digest.hexdigest()==selected['sha256'];break
  except Exception:
   if attempt==2:raise
   time.sleep(5)
 print('Anonymous full APK SHA256 verified; promoting requested preview device update.',flush=True)
 current=api('contents/update.json?ref=main');old=json.loads(base64.b64decode(current['content']))
 if old['versionCode']==54:assert old==update,'Never replace another same-code payload'
 else:
  assert old['versionCode']==53,'Concurrent newer update detected'
  mutate('contents/update.json','PUT',{'message':'chore: offer verified Moeni content recovery preview','branch':'main','sha':current['sha'],'content':base64.b64encode((ROOT/'update.json').read_bytes()).decode()},out)
 # GitHub's branch ref read can lag a just-completed Contents PUT. Verify boundedly.
 for attempt in range(8):
  confirmed=json.loads(base64.b64decode(api('contents/update.json?ref=main')['content']))
  if confirmed==update:break
  assert confirmed['versionCode'] in (53,54),'Concurrent update detected'
  if attempt==7:raise AssertionError('Update manifest did not become visible')
  time.sleep(2)
 current_readme=api('contents/README.md?ref=main');desired=Path('README.md').read_bytes()
 if base64.b64decode(current_readme['content'])!=desired:
  mutate('contents/README.md','PUT',{'message':'docs: describe verified Moeni content recovery','branch':'main','sha':current_readme['sha'],'content':base64.b64encode(desired).decode()},out)
 for ident,expected in previous.items():
  r=api('releases/'+str(ident));assert r['tag_name']==expected['tag'] and [(a['id'],a['name'],a['size'],a.get('digest')) for a in r['assets']]==expected['assets']
 assert api('releases/latest')['tag_name']=='v1.4.1'
 print('PASS: new preview published; stable Latest and previous assets preserved; device manifest code54 verified.',flush=True)
if __name__=='__main__':main()
