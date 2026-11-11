# 모에니(Moeni) 소스 프리뷰

## 범위와 조사 결과

- 요청 URL: https://moeni.net/ — 사이트 실제 표기는 **모에니 / Moeni**입니다.
- 기준: `6bf73ff749e7495db99a1f6df8501a6c65b65795` (1.4.1 / code 51), 작업 브랜치 `lycoris-moeni-preview`.
- 새 버전: **1.4.2-preview.1 / code 52**. 기존 정식 1.4.1과 과거 시험판·태그·APK를 보존합니다.
- **부분 통합: 앱에서 목록·로컬 제목 검색·작품 상세·내 목록·월~일 요일표를 지원합니다. 시청은 외부 브라우저의 원래 작품 페이지에서 직접 회차를 선택합니다.**
- **모에니의 앱 내 mpv 재생, 회차 다운로드, AI 자막 번역, 브라우저 재생 위치/시청 시간 연동, 신규 회차 알림 및 분기 조회는 구현하지 않았습니다.** 기존 다른 소스의 해당 기능은 유지합니다.

### 확인한 공개 접근 경로

2026-11-11 UTC, 일반 Chromium과 앱과 동일한 HTTP 요청 헤더를 사용해 확인했습니다. 로그인, CAPTCHA 해결, 토큰 위조, 접근 제한 우회는 하지 않았습니다.

| 경로 | 관찰 | 앱 사용 |
|---|---|---|
| `https://moeni.net/` | HTTP 200, 홈 정상 렌더링 | 사용자의 브라우저 열기 |
| `https://moeni.net/4610` | HTTP 200, 작품명·7회차·사이트 갱신일 표시 | 사용자의 브라우저 열기 |
| `/web/datalist` (api.moeni.net) | HTTP 200, 1,694개 제목/작품 ID | 최초 목록 1회, 30분 메모리 캐시, 제목 검색은 로컬 |
| `/web/main` | HTTP 200, 12개 갱신 작품 | 홈 목록 |
| `/web/4610` | HTTP 200, ID·제목·회차 수·사이트 갱신일 | 선택 작품 상세 1회 |
| `/web/week` | HTTP 200, 월~일 7개 배열 + 완결 1개 배열 | 월~일만 기존 편성표에 표시 |
| `/web/rss` | HTTP 200, 사이트가 링크한 공개 RSS | 조사만, 앱에서 중복 호출하지 않음 |
| 웹 시청 버튼 | 일반 브라우저 자동 검사에서 about:blank 이동, 영상 재생 성공 확인 불가 | 성공으로 판정하지 않음 |

사이트 플레이어는 `api.modumo.bid`의 불투명한 재생 응답을 사용합니다. 이를 복호화·재구현하거나 내부 키를 가져오지 않았습니다. 일반 HLS/MP4 재생 주소를 안정적으로 검증하지 못했으므로 앱의 mpv·다운로드·자막 엔진에 연결하지 않았습니다. 외부 브라우저의 실제 재생 성공도 미검증입니다.

### 이용 조건과 주의사항

- 사이트 `robots.txt`는 일반 크롤러에 `Disallow: /`를 명시합니다. 앱은 HTML 페이지 순회·크롤링이나 검색 봇 사칭을 하지 않습니다.
- 앱이 사용하는 API는 일반 홈페이지가 요청하는 공개 메타데이터 엔드포인트입니다. API의 robots 응답에는 내용 신호 설명 주석만 있었으며 구체적인 Allow/Disallow는 없었습니다. 이것을 재사용 허가로 간주하지 않습니다.
- 별도 제3자 통합 약관·공식 API 재사용 라이선스·영상 배포 권한은 **미확인**입니다. 공식 제휴/공식 API 지원이라고 표현하지 않습니다. API 변경·운영자 차단이 발생하면 안내하고 중단하며 재시도 루프나 우회 동작을 하지 않습니다.
- 사이트 코드·영상·암호화된 재생 목록을 앱에 포함하거나 재배포하지 않습니다. 신규 SDK/의존성/권한은 추가하지 않습니다.
- 외부 사이트의 광고·추적·로그인·재생 문제는 브라우저 및 해당 사이트의 동작에 따릅니다. 앱은 브라우저의 로그인/쿠키/시청 이력을 가져오지 않습니다.
- 공개 목록은 장르·연도 등의 필터 메타데이터를 충분히 제공하지 않습니다. 임의로 생성하지 않으며 해당 필터는 비어 있을 수 있습니다. 갱신일을 방영일로, 요일 분류를 정확한 공개 시각으로 표시하지 않습니다.

## 구현 및 보호

- `MoeniClient.kt`: 확인한 네 가지 읽기 전용 API, JSON 파서, 엄격한 숫자 ID, 4MiB 응답 제한, 제한된 타임아웃, 자동 재시도/리다이렉트 비활성화.
- `MoeniPolicy`: `moeni:<ID>` 이름 공간, 일치하는 HTTPS 작품 주소만 브라우저로 열기. 제3자·자격증명·쿼리·프래그먼트·다른 작품 주소 거부.
- `AnimeRepository`: 모에니 전용 분기만 추가. 코루틴 취소 시 interrupt 가능한 IO. 사이트의 `ep` 수치로 가짜 회차 ID·재생 주소·시청 기록을 생성하지 않음.
- `MoeniDetailScreen`: 기존 V3 Hero/상태/버튼/Classic·Glass 컴포넌트 재사용. 웹 시청 안내, 즐겨찾기, 오류·재시도. 앱 내 재생 및 다운로드 버튼 없음.
- 설정·TV 설정: 기존 값·기본 소스를 유지하고 `모에니 · 웹 시청` 선택지 추가.
- `RecommendationCatalogPolicy`: 다른 사이트의 추천·보관함·이어서 보기와 ID/URL이 섞이지 않도록 별도 검증. 모에니는 실제 회차 ID를 제공하지 않아 기존 알림 대상 판정에 추가하지 않음.
- 저장소 두 파일: 기존 구조·키·데이터 그대로, 허용 소스 집합에 `moeni`만 추가.
- 앱 ID `com.lilac.anime.enhanced`, namespace `com.lilac.anime`, 서명 및 기존 GGUF 기본값 유지. mpv, JNI, AI, Runtime, 자막, 다운로드 엔진, ViewModel 코드는 변경하지 않음.

## 검증

| 항목 | 실제 결과 |
|---|---|
| 기존 JVM 765 + 신규 23 | **788개 통과**, 실패/오류/건너뜀 0 |
| Debug / Enhanced APK | 최종 명령 **성공**, `BUILD SUCCESSFUL in 7m 22s` |
| Enhanced lint | 오류/Fatal 0, Warning **253**, Hint 20 |
| 신규 lint 경고 | `UseKtx`: `Uri.parse` 대신 `String.toUri`를 권장하는 스타일 경고 1개. 기능·보안 오류 아님 |
| Compose | 실제 컴포넌트 **5개 렌더링 및 육안 검토**. 렌더러 `Slow render action`/TimeoutException 경고 2회 후 5개 완료 |
| 엔진/네트워크/자막/ViewModel/네이티브 원본 | 별도 파일 비교 **186개 변경 없음** |
| 광범위 보호 검사 | 저장소·번역·Runtime·플레이어 등 **180개 기존 파일 동일**, 저장 파일 2개는 소스 허용 목록 추가 외 동일 |
| 기존 테스트 소스 | 기준 커밋의 테스트 파일 전부 유지 |
| 네이티브 | ARM64 **19개 SHA256 동일**, 모델·QNN 바이너리 신규 추가 없음 |
| APK | ZIP CRC·중복 엔트리·서명·앱 ID·버전·debuggable=false·ZIP/ELF 16KiB 정렬 검사 통과 |
| 업데이트 정책 | 실제 컴파일된 `PublicUpdatePolicy`: code51→52 허용, 같은 code 및 다른 서명 거절 |
| 실데이터 파서 | 앱 컴파일 코드가 실제 HTTP 응답의 목록 1,694 / 홈12 / 상세ID4610 / 요일7칸·12개를 파싱 |
| `git diff --check` | 통과 |
| 실기기 / 에뮬레이터 | ADB 기기0, `/dev/kvm` 없음. 설치·재생·PiP·AI 동시사용·성능·외부 브라우저 전환 **미검증** |

신규 23개 테스트는 ID/URL 검증, 다른 소스 격리, 잘못된 작품 상세 거절, 가짜 회차 미생성, 빈 목록·중복 제거, 이미지 fallback, 회차 수 범위, 로컬 검색 및 캐시 만료/실패 회복, 확인된 메타데이터 API 경로, 요일 배열 순서·변경 감지, 편성 라우팅, 실제 HTTP 본문·403·리다이렉트·4MiB 제한을 검증합니다. API/문자열 테스트를 영상 재생 또는 사이트 이용 허가 검증으로 해석하지 않습니다.

검증 명령 (별도 SDK/JDK를 설정하는 기존 runner 사용):

```bash
python /workspace/build-tools/run_lycoris_v2_gradle.py --no-parallel --max-workers=1 -Pkotlin.compiler.execution.strategy=in-process -Porg.gradle.java.installations.paths=/workspace/build-tools/jdk-21.0.13+9 -I /workspace/lycoris-v2-work/tools/visual_qa/export-classpath.init.gradle :app:testDebugUnitTest :app:assembleDebug :app:assembleEnhanced :app:lintEnhanced :app:exportLycorisPreviewClasspath
python tools/moeni/verify.py --apk /workspace/artifacts/lycoris-moeni-preview/Lycoris-1.4.2-preview.1-Moeni-arm64.apk --baseline-apk /workspace/artifacts/lycoris-1.4.1-unified/Lycoris-1.4.1-arm64.apk --source-commit 10c713e2962a5262878774022971b20663a21d1a --out /workspace/build-logs/moeni-preview/verification.json
git diff --check
```

- 실제 Compose 이미지: [갤러리](design-moeni/README.md)
- 상세 검증: [JSON](verification/lycoris-moeni-preview.json)
- 빌드 소스: `10c713e2962a5262878774022971b20663a21d1a`
- GitHub CI: [42967190092](https://github.com/lIlIllIIlIlIIlIIllI/private-builds/actions/runs/42967190092) — **동일 빌드 소스 커밋의 JVM·두 APK·lint 모두 성공**. 배포는 기존 인증서를 가진 로컬 검증 APK를 사용하며 CI 생성 APK를 대체 업로드하지 않습니다.

### APK 및 업데이트 호환성

- 파일: `Lycoris-1.4.2-preview.1-Moeni-arm64.apk`
- 크기: **111,053,228 bytes (111.05 MB / 105.91 MiB)**
- SHA256: `6a3d9dc88c19eaeea4045608c336ff25b48e12893263f0f94b62680e24acf318`
- 서명 SHA256: `62823547a1b9e6e42619f336e5d4a7dfe408a6de81045773a72b087305cebba5`
- code51 정식판과 같은 앱 ID·인증서, 더 높은 code52로 **업데이트 메타데이터 호환**. 실제 설치 및 데이터 유지 동작은 기기 미검증입니다.
- 정식 APK 111,053,216 bytes 대비 전체 파일은 **12 bytes 증가**했습니다. 압축 전 실제 payload는 **36,176 bytes**, 압축 payload는 **11,619 bytes 증가**했으나 기존 ZIP 정렬 패딩 변화가 대부분을 흡수했습니다. `.so` 19개는 전부 동일합니다. 작은 APK 크기 차이를 기능 제거로 해석해서는 안 됩니다.

## 배포

새 Pre-release를 생성하고, 서명 및 익명 다운로드 검증 후 기존 공개 `update.json`을 code 52로 전진시킵니다. 정식 Release의 Latest 표시는 1.4.1로 유지하며 APK 자산을 교체하지 않습니다. 현재 앱의 단일 기기 업데이트 채널에는 이 시험판이 제안됩니다. 설치 시 Android의 사용자 확인 절차는 유지합니다.

## 변경 파일 (구현 커밋)

- `android/app/build.gradle.kts`
- `android/app/src/debug/kotlin/com/lilac/anime/ui/preview/MoeniPreviews.kt`
- `android/app/src/main/kotlin/com/lilac/anime/core/schedule/Timetable.kt`
- `android/app/src/main/kotlin/com/lilac/anime/core/schedule/TimetableRepository.kt`
- `android/app/src/main/kotlin/com/lilac/anime/data/AnimeRepository.kt`
- `android/app/src/main/kotlin/com/lilac/anime/data/ContentSourceDirectory.kt`
- `android/app/src/main/kotlin/com/lilac/anime/data/MoeniClient.kt`
- `android/app/src/main/kotlin/com/lilac/anime/data/offline/MpvOfflineStore.kt`
- `android/app/src/main/kotlin/com/lilac/anime/data/offline/OfflineStore.kt`
- `android/app/src/main/kotlin/com/lilac/anime/smart/RecommendationCatalogPolicy.kt`
- `android/app/src/main/kotlin/com/lilac/anime/ui/detail/MoeniDetailScreen.kt`
- `android/app/src/main/kotlin/com/lilac/anime/ui/home/HomeScreen.kt`
- `android/app/src/main/kotlin/com/lilac/anime/ui/navigation/AppNavigation.kt`
- `android/app/src/main/kotlin/com/lilac/anime/ui/navigation/TvUi.kt`
- `android/app/src/main/kotlin/com/lilac/anime/ui/schedule/TimetableScreen.kt`
- `android/app/src/main/kotlin/com/lilac/anime/ui/settings/SourceSelectionContent.kt`
- `android/app/src/test/kotlin/com/lilac/anime/data/MoeniClientTest.kt`
- `docs/lycoris/MOENI_PREVIEW_REPORT.md`
- `docs/lycoris/design-moeni/README.md`
- `docs/lycoris/verification/moeni-public-metadata.json`
- `tools/moeni/ProbeMetadata.java`
- `tools/moeni/VerifyPublicUpdate.java`
- `tools/moeni/verify.py`
- `tools/visual_qa/previews.json`

검증 JSON·실제 Compose PNG·최종 배포 기록은 별도 검증 커밋에 추가합니다.

## 남은 제한과 후속 정리

1. 모에니의 실제 영상 재생·안정적인 공개 미디어 URL은 확인하지 못했습니다. 외부 웹 시청 연결을 앱 내 mpv 통합 완료로 표현하지 않습니다. 재생 경로와 이용 조건이 확인되기 전 다운로드·AI 자막·시청 시간 수집을 연결하지 않습니다.
2. 제3자 API 재사용 조건·영상 권한·운영 지속성은 미확인입니다. 운영자 차단 시 우회하지 않고 해당 소스의 연결을 안내해야 합니다.
3. 공통 Hero 재사용으로 포스터 탭도 원래 작품 페이지를 엽니다. 공통 이미지의 보조 설명은 ‘작품 포스터 크게 보기’로 남아 있어 해당 새 소스의 웹 열기 동작에 맞춘 접근성 문구 정리는 후속 UI 개선 대상입니다. 주된 ‘브라우저로 보기’ 버튼에는 올바른 동작과 텍스트가 표시됩니다.
4. 200% 글씨/짧은 가로 창에서는 아래 조작부와 안내를 보려면 스크롤이 필요합니다. 정적 Preview로 실제 터치·스크롤·브라우저 전환을 검증하지 않았습니다.
5. 현재 배포 과정의 CI·공개 다운로드·업데이트 채널 최종 결과는 아래 게시 기록에 후속 추가합니다.
