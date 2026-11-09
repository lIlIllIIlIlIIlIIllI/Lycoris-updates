"""Distribution only. Never build/sign APKs, replace assets, move tags, or read private source."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

REPO = "lIlIllIIlIlIIlIIllI/Lycoris-updates"
CERT = "62823547a1b9e6e42619f336e5d4a7dfe408a6de81045773a72b087305cebba5"

def command(*args):
    return subprocess.check_output(args, text=True).strip()

def api(path=""):
    endpoint = "repos/" + REPO + ("/" + path if path else "")
    endpoint += ("&" if "?" in endpoint else "?") + "verification_nonce=" + str(time.time_ns())
    return json.loads(command("gh", "api", endpoint))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert os.environ["GITHUB_REPOSITORY"] == REPO
    tag, commit, expected = (os.environ[k] for k in ("APPROVED_TAG", "APPROVED_ASSET_COMMIT", "APPROVED_METADATA_SHA256"))
    assert re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", tag)
    assert re.fullmatch(r"[0-9a-f]{40}", commit) and re.fullmatch(r"[0-9a-f]{64}", expected)
    assert command("git", "-C", ".release-assets", "rev-parse", "HEAD") == commit
    folder = Path(".release-assets/releases") / tag
    metadata = folder / "update.json"
    assert sha(metadata) == expected
    update = json.loads(metadata.read_text())
    assert update["schemaVersion"] == 1 and update["tag"] == tag
    assert update["applicationId"] == "com.lilac.anime.enhanced" and update["certificateSha256"] == CERT
    assert 1 <= update["versionCode"] <= 2147483647 and update["minSdk"] == 26
    name = update["apk"]["url"].rsplit("/", 1)[-1]
    assert re.fullmatch(r"Lycoris-[A-Za-z0-9._-]+\.apk", name)
    assert update["apk"]["url"] == f"https://github.com/{REPO}/releases/download/{tag}/{name}"
    assert update["releaseUrl"] == f"https://github.com/{REPO}/releases/tag/{tag}"
    apk = folder / name
    assert apk.stat().st_size == update["apk"]["bytes"] and sha(apk) == update["apk"]["sha256"]
    # Hosted runners supply Android SDK tools. Verify the original signer/package/version without resigning.
    sdk = Path(os.environ.get("ANDROID_HOME", "/usr/local/lib/android/sdk"))
    build_tools = sorted((sdk / "build-tools").glob("*"), reverse=True)
    tools = next(p for p in build_tools if (p / "apksigner").is_file() and (p / "aapt").is_file())
    assert CERT in command(str(tools / "apksigner"), "verify", "--print-certs", str(apk))
    badging = command(str(tools / "aapt"), "dump", "badging", str(apk))
    for value in ["name='com.lilac.anime.enhanced'", f"versionCode='{update['versionCode']}'", f"versionName='{update['versionName']}'"]:
        assert value in badging
    assets = [apk, metadata, folder / "SHA256SUMS.txt"]
    checksums = {line.split()[1]: line.split()[0] for line in assets[2].read_text().splitlines()}
    assert checksums == {p.name: sha(p) for p in assets[:2]}
    assert api()["private"] is False
    ref = api("git/ref/tags/" + tag)["object"]
    assert ref["type"] in ("tag", "commit")
    releases = [r for r in api("releases?per_page=100") if r["tag_name"] == tag]
    assert len(releases) <= 1
    notes = Path(".public-release-notes.md")
    notes.write_text(f"# Lycoris {update['versionName']} · 검토용 시험판\n\n" + update["notes"] + f"\n\n버전 코드: {update['versionCode']} · ARM64 · Android 8.0 이상\n\nGitHub 로그인 없이 APK를 다운로드할 수 있습니다. 기존 앱을 삭제하지 말고 업데이트로 설치하세요.\n\n이 APK를 설치한 뒤부터 설정 → 앱 업데이트에서 자동 확인·앱 내 다운로드를 사용할 수 있습니다. 다운로드는 사용자가 시작하며 최종 설치 확인은 Android가 처리합니다.\n\nSHA256: `{update['apk']['sha256']}`\n\n실기기 설치·재생은 별도 미검증입니다. 앱 소스·설정·API 키·서명 키는 이 저장소에 공개하지 않습니다.\n")
    if not releases:
        subprocess.run(["gh", "release", "create", tag, "--repo", REPO, "--verify-tag", "--draft", "--prerelease", "--latest=false", "--title", f"Lycoris {update['versionName']} · 로그인 없는 업데이트", "--notes-file", str(notes)], check=True)
        for _ in range(8):
            releases = [r for r in api("releases?per_page=100") if r["tag_name"] == tag]
            if releases:
                break
            time.sleep(1)
    assert len(releases) == 1
    release = api("releases/" + str(releases[0]["id"]))
    assert release["prerelease"]
    for path in assets:
        existing = next((a for a in release["assets"] if a["name"] == path.name), None)
        if existing:
            assert existing["size"] == path.stat().st_size and existing["digest"] == "sha256:" + sha(path)
        else:
            assert release["draft"], "Never change an already published release"
            subprocess.run(["gh", "release", "upload", tag, str(path), "--repo", REPO], check=True)
    release = api("releases/" + str(release["id"]))
    for path in assets:
        a = next(a for a in release["assets"] if a["name"] == path.name)
        assert a["state"] == "uploaded" and a["size"] == path.stat().st_size and a["digest"] == "sha256:" + sha(path)
    if release["draft"]:
        subprocess.run(["gh", "release", "edit", tag, "--repo", REPO, "--draft=false", "--prerelease", "--latest=false"], check=True)
    assert not api("releases/" + str(release["id"]))["draft"]
    # Advance main/update.json only after the actual APK has been published and its server digest verified.
    files = api("contents?ref=main")
    current = next((x for x in files if x["name"] == "update.json"), None)
    payload = {"message": "chore: publish update metadata for " + tag, "branch": "main", "content": base64.b64encode(metadata.read_bytes()).decode()}
    if current:
        previous = json.loads(base64.b64decode(api("contents/update.json?ref=main")["content"]))
        assert previous["versionCode"] <= update["versionCode"], "Never downgrade public update metadata"
        if previous["versionCode"] == update["versionCode"]:
            assert previous == update, "Never replace metadata for the same app version"
            print(update["releaseUrl"])
            return
        payload["sha"] = current["sha"]
    request = Path(".public-update-request.json")
    request.write_text(json.dumps(payload))
    subprocess.run(["gh", "api", "--method", "PUT", "repos/" + REPO + "/contents/update.json", "--input", str(request), "--silent"], check=True)
    assert json.loads(base64.b64decode(api("contents/update.json?ref=main")["content"])) == update
    print(update["releaseUrl"])

if __name__ == "__main__":
    main()
