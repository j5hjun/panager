---
description: 새 기능 개발 시 따라야 할 전체 워크플로우 (요구사항 → 디자인 → 계획 → 구현 → PR)
---

# 기능 개발 워크플로우

새로운 기능을 개발할 때 따라야 할 전체 프로세스입니다.

## 1. 구현 대상 선정 및 브랜치 생성

개발을 시작하기 전에 무엇을 구현할지 명확히 하고, 그에 맞는 작업 브랜치를 생성합니다. 모든 작업은 명확한 요구사항을 기반으로 시작되어야 합니다.

1. **요구사항(SRS) 분석 및 대상 선정**:
   - `docs/SRS_*.md` 문서를 검토하여 구현 대상을 찾습니다.
     - **FR (기능 요구사항)**: `FR-001` 등 ID와 내용을 확인합니다.
     - **NFR (비기능 요구사항)**: 성능, 보안 등 제약사항을 확인합니다.
   - 만약 SRS에 내용이 없거나 부족하다면, 먼저 SRS를 작성하거나 업데이트하여 요구사항을 구체화합니다. (IEEE 830 표준 참고)

2. **계획서 ID 확인**:
   - `docs/plans/`의 마지막 계획를 확인하여 현재 진행 흐름에 맞는 다음 기능인지 파악합니다.

3. **브랜치 생성**:
   - 할당받은 ID와 기능명을 조합하여 브랜치를 생성합니다.
   ```bash
   git checkout -b feat/PLAN_XXX-[기능명]
   # 예: git checkout -b feat/PLAN_009-calendar-integration
   ```

## 2. 디자인 문서 작성 (Design Options)

구현 방법을 결정하기 위해 AI가 여러 대안을 분석합니다.

**참조 템플릿**: `docs/templates/TEMPLATE_design_options.md`
**작성 위치**: `docs/designs/DO_XXX_[기능명].md`
예: `docs/designs/DO_009_calendar_integration.md`

**프로세스**:
1. 사용자가 기능 목표 설명
2. **AI가 최소 3가지 구현 방안 조사 및 비교**
3. 각 방안의 장단점, 구현 난이도, 예상 시간 분석
4. AI 추천 및 이유 제시
5. **사용자가 방안 선택**
6. 선택한 방안을 문서 하단 "결정" 섹션에 기록

**중요**: 이 단계를 건너뛰면 구현 후 "다른 방법이 더 좋았을 텐데"라는 후회가 생길 수 있음!

## 3. 기능 계획서 작성

구현할 기능이 아키텍처에 맞게 연결될 수 있도록 작성합니다.

**작성 위치**: `docs/plans/PLAN_XXX_[기능명].md`
예: `docs/plans/PLAN_015_user_preferences.md`

**참조 문서**:
- `docs/templates/SKILL.md`
- `docs/templates/plan-template.md`

## 4. 기능 계획서 기반으로 구현

**중요**: 서버 실행 시 구현한 기능이 main.py에 연결되어 있는지 최종 확인합니다.

## 5. CI 사전 검증 (모든 Phase 완료 후)

모든 페이즈가 완료되면, PR 생성 전 로컬 환경에서 CI 요구사항을 충족하는지 최종 확인합니다.

**참조 문서**:
- `.github/workflows/ci.yml`

## 6. Git 커밋 및 푸시

반복적인 커밋과 푸시를 통해 작업을 저장합니다.

**참조 문서**:
- `.agent/workflows/git-workflow.md`

## 7. PR 생성
사용자가 제공된 제목과 내용을 보고 직접 PR 생성합니다.

**PR 제목 형식**:
```
feat: [PLAN_XXX] [기능 요약]
# 예: feat: PLAN_013 외부 캘린더 연동 (Google)
```

**PR 템플릿**:
- `.github/pull_request_template.md`


## 8. 머지 후 정리

- **기능 계획서 업데이트**: 최종 완료 확인
- **main 브랜치 동기화**:
```bash
git checkout main
git pull origin main
```
- **로컬 브랜치 삭제**:
```bash
git branch -d feat/PLAN_XXX-[기능명]
```