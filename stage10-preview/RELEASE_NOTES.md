# Lycoris 1.4.1-preview.10 · Stage10 검토판

**[업데이트용 APK 다운로드 — AI 포함](https://github.com/lIlIllIIlIlIIlIIllI/Lycoris-updates/releases/download/v3-ai-stage10-preview.10/Lycoris-1.4.1-preview.10-Stage10-AI-Experimental-arm64.apk)** · [일반 APK — SDK 미포함](https://github.com/lIlIllIIlIlIIlIIllI/Lycoris-updates/releases/download/v3-ai-stage10-preview.10/Lycoris-1.4.1-preview.10-Stage10-arm64.apk)

기존 앱을 삭제하지 말고 APK 업데이트로 설치하세요. **두 APK 모두 기존 GGUF가 기본값**입니다. LiteRT는 AI 설정에서 번역 제공자 `로컬 AI` → `LiteRT 실험`을 직접 선택하고 모델을 준비할 때만 실행합니다. 모델 weights는 APK에 없습니다. Source code ZIP/배포용 part 파일은 설치 APK가 아닙니다.

## 구현
- 공식 LiteRT-LM0.16.0 선택형 엔진, 분리된 비공개 SDK 워커, 파일/실시간 자막 공통 로컬 경로.
- Hugging Face 검색/파일 가져오기, immutable revision·크기·SHA256 검사, 실제 Range 이어받기, 부분 파일 정리, 사용 중인 모델 삭제 차단.
- 명시적 모델은 같은 모델의 GPU→CPU 초기화만 대체합니다. Auto는 개별 승인 후보와 초기화 전 GGUF 복구만 허용합니다. 자막을 몰래 클라우드로 보내지 않습니다.
- 기존 모델·Runtime ZIP v3·JNI 취소·자막 캐시·API 키·테마·다운로드·기록·mpv를 보존합니다.

## 검증
- 일반/AI 각각 JVM744개, failure/error/skipped0. 기존693개와88 test 파일 보존.
- 일반/AI Debug·Enhanced 빌드, lint Error/Fatal0 (일반 Warning247, AI Warning249, Hint20; SDK module HandlerLeak Warning1).
- [동일 source의 두 variant GitHub CI](https://github.com/lIlIllIIlIlIIlIIllI/private-builds/actions/runs/42791692271) 성공.
- 실제 GGUF host JNI16+9, 실제 공식 SDK Linux CPU 초기화/추론/취소·재요청, 실제 public HF347,251,840byte 모델의 HTTP206/SHA256 검증.
- 실제 Compose 컨트롤15개 렌더링. 기기 스크린샷이 아닙니다.
- 실제 APK에 provider·비공개 워커 포함 확인. 일반 APK는 SDK/provider/worker 미포함. 기존 native18개는 모두 바이트 동일합니다.
- 서명·CRC·16KiB ZIP 정렬/추가 ELF LOAD 검사 통과.

## 반드시 알아둘 제한
- **Android 실기기 설치·재생·PiP·회전·AI 동시 실행·GPU/발열/배터리·장시간 메모리는 미검증**입니다. Android CPU/GPU 성공으로 표시하지 않습니다.
- **NPU 사용 불가**: 검증한 vendor SDK·SoC compiled model pipeline이 없습니다. QNN 바이너리를 포함하지 않았습니다. 하드웨어 감지/초기화 성공은 실제 가속기 telemetry가 아니며 N/A로 표시합니다.
- 작은 Qwen0.6B 시험 모델은 한국어 자막 품질이 부족했습니다. production 기본 모델로 권장하지 않습니다. 기존 GGUF 모델/설정은 자동 교체하지 않습니다.
- Linux CPU 수치는 Android 성능이 아닙니다. SDK·모델·출력 설정이 이전과 달라 직접 속도 향상을 주장하지 않습니다. 이미 warm-up된 GGUF와 SDK 모델이 동시에 메모리에 남을 수 있습니다.
- 두 파일은 같은 appId/서명/code50이므로 별도 앱이 아닙니다. 앱 내 업데이트는 code48/49→50을 지원하며 같은50의 일반↔AI 전환은 앱 내 정책상 제공하지 않습니다. 실제 설치는 미검증입니다.

## 기기에서 업데이트
사용자 승인에 따라 APK 게시 검증 후 공개 `main/update.json`을 **AI 포함 APK/code50**으로 갱신합니다. 기존 앱의 설정 → 앱 업데이트 → 지금 확인에서 조회할 수 있으며 기존 자동 확인 설정은 유지합니다. 다운로드 후 설치 확인은 Android가 처리합니다. GitHub 로그인이 필요 없습니다. 기존 Pre-release/정식 Release/태그/APK는 덮어쓰지 않습니다.

## 파일
- AI `Lycoris-1.4.1-preview.10-Stage10-AI-Experimental-arm64.apk` — 111,036,844bytes (105.89MiB), SHA256 `267d9f0494c5c87b62bcad47c7bdbe355a56597de9c8cd48d437cbab2eb1e901`
- 일반 `Lycoris-1.4.1-preview.10-Stage10-arm64.apk` — 88,260,363bytes (84.17MiB), SHA256 `b3b19cc29dbc25b20e2ec5dcab7e73bdfde8c24f39479fe6b4908014c9932ecd`
- appId `com.lilac.anime.enhanced` / namespace `com.lilac.anime` / versionCode50 / Android8+ ARM64.
- 기존 signer `62823547a1b9e6e42619f336e5d4a7dfe408a6de81045773a72b087305cebba5` 유지. code49→50로 메타데이터상 업데이트 호환.
- [실제 APK source commit](https://github.com/lIlIllIIlIlIIlIIllI/private-builds/commit/dcd67f844cf65185e0d1bb5932395b39fc2a5601) — 소스 비공개 유지
- [전체 A–Q 보고서](https://github.com/lIlIllIIlIlIIlIIllI/private-builds/blob/lycoris-stage10-ai-acceleration/docs/lycoris/STAGE10_AI_ACCELERATION_REPORT.md)
- [실제 Compose 갤러리](https://github.com/lIlIllIIlIlIIlIIllI/private-builds/blob/lycoris-stage10-ai-acceleration/docs/lycoris/design-stage10/README.md)
- [Build info](https://github.com/lIlIllIIlIlIIlIIllI/Lycoris-updates/releases/download/v3-ai-stage10-preview.10/Lycoris-Stage10-BUILD-INFO.json) · [SHA256SUMS](https://github.com/lIlIllIIlIlIIlIIllI/Lycoris-updates/releases/download/v3-ai-stage10-preview.10/SHA256SUMS.txt)

Inspired by LilacAnime. 원본 고지를 유지합니다. LiteRT-LM0.16 Apache2 LICENSE/THIRD_PARTY_NOTICE를 포함하며 모델 weights·QNN proprietary binaries·키는 포함하지 않습니다.
