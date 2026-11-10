# Lycoris 1.4.1 · 통합 Enhanced

**APK 하나만 받으세요:** `Lycoris-1.4.1-arm64.apk` · 111.05 MB · Android8+/ARM64.
기존 앱은 삭제하지 말고 업데이트로 설치하세요. 같은 앱 ID/기존 인증서와 code50→51을 검사했습니다. 실제 기기 설치는 미검증입니다.

변경 내용

- 일반/AI 별도 배포를 하나로 통합했습니다. GGUF/llama.cpp가 로컬 기본이며 LiteRT-LM0.16 사용 허용은 기본 OFF입니다. 모델 가중치는 APK에 넣지 않습니다.
- LiteRT OFF 시 새 요청 차단·진행 요청 취소·worker 종료 확인·GGUF 복귀를 추가했습니다. 모델·Runtime·API 키·기존 설정·기록·다운로드는 보존합니다. 정리 미확인 시 재시작을 안내합니다.
- 검정·차콜·Rose/진홍색 Classic/Glass의 가독성·홈 Hero/포스터·회차·공통 버튼/상태 표현을 정리했습니다.
- 업데이트에 정식/시험판·용량·마지막 확인 성공 시각·속도·취소·재시도·공간 안내를 추가했습니다. 취소는 상단에서도 가능합니다. APK 이어받기는 미지원이며 재시도 때 처음부터 SHA256을 검사합니다.
- 기존 mpv/Surface, 자막·번역 캐시, 다운로드/저장소, 앱 ID/서명을 유지했습니다. Android 설치 승인 및 보안 검사를 우회하지 않습니다.

자동 검증

- JVM **765개 통과**, 실패/오류/skipped0. 기존744개 + 신규21개.
- Debug/Enhanced 빌드, GitHub Actions 성공. Enhanced lint 오류0, 경고252/Hint20.
- 실제 Compose/Layoutlib **71개 렌더 성공**. 첨부 Preview ZIP은 정적 fixture이며 실제 기기 캡처가 아닙니다.
- 기존19개 native library SHA 동일, APK signer/CRC 및16KiB ZIP/ELF 정렬 통과.
- SHA256: `59adaf514912c679507c0ee2551a5717f4d4e905b00a804363b70d76a07d1fb9`
- 빌드 소스: `e2522e142e8b3a65406520c4ad7d4d0a09301350`.

알려진 제한

- Galaxy 실기기 설치·재생/PiP/자막·GPU 및 업데이트 설치/성능은 미검증입니다. Linux CPU SDK 시험을 Android GPU/NPU 성공으로 표시하지 않습니다.
- LiteRT는 선택형 실험 기능입니다. 직접 지정한 `.litertlm`만 실행하며 NPU는 비활성화입니다. 기존 GGUF 모델/Runtime이 기본이고 GGUF 자체의 기존 동작은 유지합니다.
- [Figma 초안](https://www.figma.com/design/JjHUqsBKnUHjeobZZnN24U)에 3방향과30개 폰 화면을 만들었으나 Starter MCP 한도로 텍스트 auto-height 보정·최종 QA·태블릿 Figma 프레임은 미완료입니다. APK의 실제 Compose71개와 구분합니다.
- 앱 시작 시 자동 확인은 기존 최대6시간/실패30분 제한입니다. 자동 설치나 정확한 시각의 백그라운드 업데이트는 제공하지 않습니다.

이전 정식/시험판 Release·태그·APK는 보존합니다. 공개 배포 후 정확한 파일의 익명 다운로드/SHA를 확인한 다음 `main/update.json`을 code51로 올립니다.
