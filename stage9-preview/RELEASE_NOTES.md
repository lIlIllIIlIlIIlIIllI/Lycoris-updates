Stage9 검토용 Enhanced APK입니다. **기존 GGUF 번역 엔진과 기존 모델/Runtime 선택을 기본값으로 유지합니다.**

**[APK 직접 다운로드](https://github.com/lIlIllIIlIlIIlIIllI/Lycoris-updates/releases/download/v3-ai-stage9-preview.9/Lycoris-1.4.1-preview.9-Stage9-arm64.apk)** — APK 파일을 선택하세요. Source code ZIP은 Android 설치 파일이 아닙니다.

### 변경 사항
- AI 설정에 설치된 로컬 모델로 실행하는4문장 성능 진단을 추가했습니다. 세션 준비/문장 지연/CPU·PSS, 지원 Runtime의 native timing을 표시합니다.
- Runtime ZIP의 manifest 경로 탈출과 기존 파일 선삭제 위험을 막고 설치 실패 rollback을 추가했습니다. 기존 모델·설정·API 키·다운로드·기록을 초기화하지 않습니다.
- 별도 선택형 CPU Runtime0.3에 협력 취소/진단 export를 추가했습니다. 기존 v3 팩도 계속 지원합니다.
- LiteRT-LM CPU 실험과 별도 워커의 시작 격리를 소스에서 구현했지만 **이 배포 APK에는 LiteRT/QNN SDK·실험 provider/worker가 포함되지 않습니다.** GPU/NPU 가속 성공을 주장하지 않습니다.

### 선택형 Runtime
[CPU Runtime0.3 ZIP](https://github.com/lIlIllIIlIlIIlIIllI/Lycoris-updates/releases/download/v3-ai-stage9-preview.9/Lycoris-LocalAI-Stage9-CPU-arm64-0.3.0-preview.1.zip)은 명시적으로 가져와 선택하는 실험 파일입니다. 자동 설치/기존 팩 교체/모델 재다운로드는 하지 않습니다. 새 취소 export는 이 팩에서 사용합니다. 이미 다른 native 팩을 로드한 프로세스의 재시작 필요 정책은 유지합니다.

Linux의 동일 GGUF fixture에서 기존 작업이 끝날 때까지32~40초 기다리던 취소 요청이 새 팩에서는 약8~32ms 뒤 반환했습니다. **Android 실기기 결과가 아닙니다.** 일반 HY-MT 문장 지연은 약8% 증가한 표본도 있어 토큰 생성 속도 개선을 권장하지 않으며 기본 Runtime에 적용하지 않았습니다. 새 팩/모델 weights는 APK에 내장하지 않습니다.

### 검증
- 로컬 JVM **693개**, 실패/오류/생략0. 기존673개와 원본 테스트 파일을 보존했습니다.
- [동일 source의 GitHub Android CI](https://github.com/lIlIllIIlIlIIlIIllI/private-builds/actions/runs/42764117089) 성공. CI artifact ZIP은 이 환경에서403이어서 원격 XML 개수를 별도로 확인했다고 주장하지 않습니다.
- 정상 Debug/Enhanced·opt-in lab 빌드/lint 통과. 정상 lint Error/Fatal0(경고239, 힌트20).
- 기존 native18개 SHA256 일치, JNI16+9, HY-MT 실제 샘플8, template8, Compose41 렌더/기준 PNG41개 일치.
- APK 서명·CRC·16KiB ZIP 정렬 검사 통과. dev JDK/NDK/Robolectric·SDK·모델 weights는 APK에 포함하지 않았습니다.

### 설치 호환성 및 미검증
- `1.4.1-preview.9` / versionCode `49` / ARM64 / Android8+.
- package `com.lilac.anime.enhanced`와 기존 signer를 유지했습니다. code48→49로 **메타데이터상 업데이트 호환**입니다. 실제 기기에 업데이트 설치한 결과는 미검증입니다.
- Galaxy S24 Ultra·Tab S9 Ultra 실제 영상/음성, ASS/Text, PiP·회전·백그라운드, AI 동시 재생, 발열·배터리, 실제 다운로드/알림은 **실기기 미검증**입니다.
- 실제 기기가 없고 software emulator도 디스크 요구로 부팅하지 못해 JVM/Robolectric/실제 Compose 렌더링/MockWebServer 및 Linux 실제 모델로 대체했습니다.
- 선택형 CPU 팩의 Android 추론, LiteRT Android CPU/GPU/NPU, QNN 실제 실행은 미검증/보류입니다. 정식 Release가 아닌 검토용 Pre-release입니다.
- 기존 Release·태그·정식 v1.4.0·자동 업데이트 manifest를 덮어쓰지 않습니다. 이번 파일은 직접 다운로드하는 시험판입니다.

### 파일 정보
- APK: `Lycoris-1.4.1-preview.9-Stage9-arm64.apk` / `88,211,211`bytes (84.12MiB)
- APK SHA256: `89d028d3536727ed4a45eedd32b7df09a767e4a0aaf84dce456c15214113d627`
- 기존 signer SHA256: `62823547a1b9e6e42619f336e5d4a7dfe408a6de81045773a72b087305cebba5`
- 실제 APK build source: [4af8fb07ac2d762b00195d2a12d64d3adcd2510d](https://github.com/lIlIllIIlIlIIlIIllI/private-builds/commit/4af8fb07ac2d762b00195d2a12d64d3adcd2510d) (소스 비공개 유지)
- [전체 분석/검증 보고서](https://github.com/lIlIllIIlIlIIlIIllI/private-builds/blob/lycoris-stage9-ai-optimization/docs/lycoris/STAGE9_AI_OPTIMIZATION_REPORT.md)
- [Build receipt](https://github.com/lIlIllIIlIlIIlIIllI/Lycoris-updates/releases/download/v3-ai-stage9-preview.9/Lycoris-Stage9-BUILD-INFO.json) · [SHA256SUMS](https://github.com/lIlIllIIlIlIIlIIllI/Lycoris-updates/releases/download/v3-ai-stage9-preview.9/SHA256SUMS.txt)

Inspired by LilacAnime. 기존 고지를 유지합니다. CPU 팩에는 llama.cpp/ggml MIT·NDK·vendor·HY-MT template 고지를 포함했고 모델 weights/QNN proprietary binaries는 포함하지 않았습니다.
