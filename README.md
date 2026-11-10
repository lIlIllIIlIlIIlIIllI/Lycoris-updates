# Lycoris — APK & Updates

Lycoris Android의 **공개 APK 배포 및 업데이트 정보 전용 저장소**입니다. 앱 소스, 사용자 데이터, API 키와 서명 키는 포함하지 않습니다.

## 다운로드

**[APK 다운로드 · Releases](https://github.com/lIlIllIIlIlIIlIIllI/Lycoris-updates/releases)** — GitHub 로그인 없이 사용할 수 있습니다. **최신 정식: [Lycoris 1.4.1 · 통합 Enhanced APK](https://github.com/lIlIllIIlIlIIlIIllI/Lycoris-updates/releases/tag/v1.4.1)**. 일반/AI 별도 APK 없이 하나만 배포합니다. 기존 GGUF 기본, LiteRT-LM 사용 허용은 기본 OFF입니다. Android 실기기 CPU/GPU·재생은 미검증이고 NPU는 비활성화입니다.

- ARM64 Android 8.0(API26) 이상. 기존 Lycoris Enhanced와 같은 앱 ID/서명을 사용합니다.
- 앱을 삭제하지 말고 APK를 기존 앱 위에 업데이트로 설치하세요.
- 처음 한 번 **1.4.1-preview.3(code43)** 이상을 설치하면 **설정 → 앱 업데이트**에서 새 버전을 확인·다운로드할 수 있습니다.
- 홈 진입 시 최대 6시간에 한 번 자동 확인합니다. 자동 확인은 설정에서 끌 수 있습니다.
- APK 다운로드는 사용자가 눌렀을 때 시작합니다. SHA256·파일 크기·패키지·기존 서명·상위 버전을 검사합니다.
- 설치 권한과 최종 설치 확인은 Android가 처리합니다. Play Protect 등 보안 검사는 변경하지 않습니다.
- 같은/구버전 APK는 앱 내부 설치 검사에서 거절됩니다. 이미 최신일 때 다시 다운로드할 필요가 없습니다.

## 공개 범위

이 저장소에는 APK, `update.json`, SHA256 체크섬, 사용 안내 및 배포 자동화 구성만 게시합니다. 공개된 APK는 누구나 받을 수 있습니다.

앱 코드 저장소와 기존 배포 이력은 별도로 유지합니다. 이 저장소의 소스 ZIP은 배포 구성일 뿐 Android 앱 소스가 아닙니다.

## 확인 범위

빌드·JVM 테스트·APK 서명 및 공개 다운로드를 확인합니다. 실기기 설치/재생·Play Protect 판정·배터리/성능은 별도 기기 검증이 필요합니다.
