# Lycoris 1.4.2-preview.5 · 시험판

- 홈에서 회차 목록을 열고 재생할 수 있습니다.
- 앱을 새로 연 직후에도 이어보기를 사용할 수 있도록 로딩 경로를 보완했습니다.
- 다운로드한 영상의 일본어 음성을 Whisper로 분석해 자막 시간차를 계산합니다. 미리 보고 적용하거나 되돌릴 수 있습니다.
- 태블릿 자막 패널을 열 때 영상 면의 크기가 바뀌는 문제와 보정 미리 보기에서 발생한 Android ICU 정규식 크래시를 수정했습니다.

PC 측에서 제공한 휴대폰 에뮬레이터 결과는 합성 영상의 -2400 ms 보정과 미리 보기·적용·원복 확인입니다. 같은 최종 커밋의 태블릿 가로 화면에서는 자막 패널이 정상적으로 열렸습니다. 216초 합성 일본어 영상에서 -2400 ms를 찾아 00:29에 실제 테스트 자막 문장이 표시되는 것과 적용·원복을 확인했습니다. Windows의 Debug·Enhanced 빌드, Lint, 관련 JVM 테스트 19개도 통과했습니다. 이 결과는 PC에서 실행한 에뮬레이터 검증입니다.

JVM 테스트 1020개 통과, Enhanced 빌드 통과, Lint 오류 0개, 동일 커밋의 GitHub CI 통과. ARM64, 버전 코드 56. 기존 인증서로 서명했습니다.

APK 크기 111,282,604바이트. SHA-256 `4a0b38eafbc476621a4be0aa06a6953357e2760b672b6586e46ced30c9528232`.

[빌드 소스](https://github.com/lIlIllIIlIlIIlIIllI/private-builds/commit/4312bd989fab55604eabfd2e6781539387274f50) · [GitHub CI](https://github.com/lIlIllIIlIlIIlIIllI/private-builds/actions/runs/44907234943)
