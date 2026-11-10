"""Publish approved immutable binaries; never build, sign, or advance main/update.json."""
from pathlib import Path
import hashlib
import json
import os
import subprocess

REPO = 'lIlIllIIlIlIIlIIllI/Lycoris-updates'
TAG = 'v3-ai-stage9-preview.9'
RELEASE_ID = 440005853
CERT = '62823547a1b9e6e42619f336e5d4a7dfe408a6de81045773a72b087305cebba5'
APK_SHA = '89d028d3536727ed4a45eedd32b7df09a767e4a0aaf84dce456c15214113d627'
SOURCE = '4af8fb07ac2d762b00195d2a12d64d3adcd2510d'
ROOT = Path('stage9-preview')

def cmd(*args):
    return subprocess.check_output(args, text=True).strip()

def api(path):
    return json.loads(cmd('gh', 'api', 'repos/' + REPO + '/' + path))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert os.environ['GITHUB_REPOSITORY'] == REPO
    assert os.environ['GITHUB_REF'] == 'refs/heads/stage9-preview-delivery'
    before_main = api('git/ref/heads/main')['object']['sha']
    before_update = api('contents/update.json?ref=main')['sha']
    all_releases = api('releases?per_page=100')
    previous = {r['id']: [(a['id'], a['name'], a['size'], a.get('digest')) for a in r['assets']]
                for r in all_releases if r['id'] != RELEASE_ID}
    info = json.loads((ROOT / 'Lycoris-Stage9-BUILD-INFO.json').read_text())
    assert info['source_commit'] == SOURCE
    assert info['signer_sha256'] == CERT and info['application_id'] == 'com.lilac.anime.enhanced'
    assert info['version_code'] == 49 and info['version_name'] == '1.4.1-preview.9'
    assert info['gguf_default'] and not info['public_sdk_binaries']
    assert info['tests'] == {'tests': 693, 'failures': 0, 'errors': 0, 'skipped': 0}
    apk = ROOT / info['apk']
    assert sha(apk) == APK_SHA and apk.stat().st_size == 88211211
    files = [apk, ROOT / 'Lycoris-LocalAI-Stage9-CPU-arm64-0.3.0-preview.1.zip', ROOT / 'Lycoris-Stage9-BUILD-INFO.json']
    checksums = {line.split()[1]: line.split()[0] for line in (ROOT / 'SHA256SUMS.txt').read_text().splitlines()}
    assert checksums == {p.name: sha(p) for p in files}
    sdk = Path(os.environ['ANDROID_HOME'])
    tools = next(p for p in sorted((sdk / 'build-tools').glob('*'), reverse=True)
                 if (p / 'apksigner').is_file() and (p / 'aapt').is_file())
    assert CERT in cmd(str(tools / 'apksigner'), 'verify', '--print-certs', str(apk))
    badging = cmd(str(tools / 'aapt'), 'dump', 'badging', str(apk))
    for part in ["name='com.lilac.anime.enhanced'", "versionCode='49'", "versionName='1.4.1-preview.9'"]:
        assert part in badging
    release = api('releases/' + str(RELEASE_ID))
    assert release['tag_name'] == TAG and release['prerelease']
    files.append(ROOT / 'SHA256SUMS.txt')
    for path in files:
        existing = next((a for a in release['assets'] if a['name'] == path.name), None)
        if existing:
            assert existing['size'] == path.stat().st_size and existing['digest'] == 'sha256:' + sha(path)
        else:
            assert release['draft'], 'Never alter a published release'
            subprocess.run(['gh', 'release', 'upload', TAG, str(path), '--repo', REPO], check=True)
    release = api('releases/' + str(RELEASE_ID))
    assert len(release['assets']) == len(files)
    for path in files:
        asset = next(a for a in release['assets'] if a['name'] == path.name)
        assert asset['state'] == 'uploaded' and asset['size'] == path.stat().st_size
        assert asset['digest'] == 'sha256:' + sha(path)
    if release['draft']:
        subprocess.run(['gh', 'release', 'edit', TAG, '--repo', REPO, '--draft=false',
                        '--prerelease', '--latest=false', '--notes-file', str(ROOT / 'RELEASE_NOTES.md')], check=True)
    assert not api('releases/' + str(RELEASE_ID))['draft']
    assert api('git/ref/heads/main')['object']['sha'] == before_main
    assert api('contents/update.json?ref=main')['sha'] == before_update
    for ident, expected in previous.items():
        current = api('releases/' + str(ident))
        assert [(a['id'], a['name'], a['size'], a.get('digest')) for a in current['assets']] == expected
    print('Published approved preview; original releases and update channel unchanged.')

if __name__ == '__main__':
    main()
