# Lycoris 1.4.2-preview.4 · 검토용 시험판

사이트 연결 수정과 Stage 13 온라인 자막 확장을 함께 배포합니다.

- SubDL v2(선택형v1)·SubSource 검색/다운로드, 한국어 기본·일본어/영어 선택, 명시적 IMDb/TMDB 타입 검색, 안전한 ZIP·인코딩 검사.
- 다운로드한 파일은 미리보기 후 직접 적용합니다. 적용한 파일만 재실행 시 복원합니다. 기존 AI 번역 설정과 원문 파일을 유지합니다.
- 설정 → 자막 → 온라인 자막 제공처에서 **각 서비스의 본인 API 키**를 입력합니다. 키는 앱에 직접 입력하고 채팅/로그로 보내지 마세요.
- ohli24.net/RE:Anime .cz/Linkani 메타데이터, 검증된 제목·포스터 대체를 포함합니다. 모에니/사이트 간 보관함 변경도 보존했습니다.

## 검증

JVM **1013개 성공**, Debug/Enhanced 빌드·Enhanced lint 오류0, 실제 Compose 컴포넌트 렌더링9개. 별도 GitHub CI 성공.
앱 ID `com.lilac.anime.enhanced`, code55, ARM64, 기존 인증서 일치. 기존 앱을 삭제하지 말고 업데이트로 설치하세요.
기존 GGUF 기본값, LiteRT 선택형 OFF, 네이티브19개 동일. 기존 정식1.4.1 및 이전 Preview 자산/태그를 보존합니다.

## 미검증과 제한

- **사용자 API 키가 없어 인증된 SubDL/SubSource 실서비스 검색·다운로드는 미검증**입니다. 무인증401과 공식 문서 확인은 성공한 자막 검색이 아닙니다. API 연결은 실험 기능입니다.
- 실기기 설치/업데이트/영상 재생/자막 부착/AI 생성 품질/회전/성능 미검증. 가상 목업을 실기기 캡처로 사용하지 않았습니다.
- SubtitleCenter는 API 확인 필요, AJATT는 파일별 이용 조건 확인 전 자동 연동 보류. 기존 수동 자막 가져오기를 사용하세요.
- 한국어가 없으면 사용자가 일본어/영어 검색으로 바꿉니다. 모든 판본·OVA·특별편을 자동 확정하지 않습니다. ZIP/파일 크기 제한 및 정확한 허용 도메인 정책으로 일부 제공 파일은 지원하지 않을 수 있습니다.
- Miruro API403 미해결. AniList 공식API403을 성공으로 표시하지 않고 검증된 공개 ID 기반 제목 대체만 사용합니다. 모에니의 앱 내 영상 재생은 추가하지 않았습니다.

APK SHA256: `3caa888f5502ab45e2edb0a967dda92ec4abdf4f5ee9c6b49342072073c3b6d9`

APK 빌드 소스: https://github.com/lIlIllIIlIlIIlIIllI/private-builds/commit/2413e9d933c5de5a3c2194c9db1aec1c8a72a439

보고서: https://github.com/lIlIllIIlIlIIlIIllI/private-builds/blob/lycoris-stage13-subtitle-providers/docs/lycoris/STAGE13_SUBTITLE_PROVIDERS_REPORT.md

CI: https://github.com/lIlIllIIlIlIIlIIllI/private-builds/actions/runs/43651012521
