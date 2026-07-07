# 넵무새 기능 명세 (MVP)

서비스명: **넵무새 - 성공적인 사회초년생활 카톡 코치**

## 목표 시나리오

1. 교수님 지시 메시지에 답장 초안 생성
2. 상사 메시지의 어려운 용어(IP 등) 해설 + 답장 동시 제공
3. 일정 충돌 시 정중한 역제안 문구 생성
4. 읽씹 상황 공손 리마인드
5. 합의사항 책임소재 확인 문구 생성
6. 자료 지연 사과 + 만회 계획 문구 생성

## 툴 목록

1. `analyze_and_rewrite_reply`
2. `explain_message_terms`
3. `generate_polite_followup`
4. `generate_confirmation_message`
5. `generate_recovery_apology`

## 출력 설계 원칙

- 항상 바로 복붙 가능한 답장 문구 포함
- 리스크는 점수+유형+수정 가이드로 구조화
- 사회초년생/대학원생 기준 쉬운 문장 우선
- 톤 옵션은 짧은/표준/매우공손 3단 구성
