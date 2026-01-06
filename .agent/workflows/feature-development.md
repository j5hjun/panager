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
   - `docs/plans/PLAN_master.md`를 확인하여 현재 진행 흐름에 맞는 다음 기능인지 파악합니다.
   - 신규 기능이라면 Master Plan에서 다음 사용 가능한 ID(예: P-005)를 할당받습니다.

3. **브랜치 생성**:
   - 할당받은 ID와 기능명을 조합하여 브랜치를 생성합니다.
   ```bash
   git checkout -b feat/[계획서ID]-[기능명]
   # 예: git checkout -b feat/p-005-calendar-integration
   ```

## 2. 디자인 문서 작성 (Design Options)

구현 방법을 결정하기 위해 AI가 여러 대안을 분석합니다.

**참조 템플릿**: `docs/templates/TEMPLATE_design_options.md`
**작성 위치**: `docs/designs/DO_[기능명].md`

**프로세스**:
1. 사용자가 기능 목표 설명
2. **AI가 최소 3가지 구현 방안 조사 및 비교**
3. 각 방안의 장단점, 구현 난이도, 예상 시간 분석
4. AI 추천 및 이유 제시
5. **사용자가 방안 선택**
6. 선택한 방안을 문서 하단 "결정" 섹션에 기록

**중요**: 이 단계를 건너뛰면 구현 후 "다른 방법이 더 좋았을 텐데"라는 후회가 생길 수 있음!

## 3. 통합 계획서 확인

// turbo
```bash
cat docs/plans/PLAN_master.md | head -150
```

- **현황 파악**: 전체 프로젝트 진행 상황 확인
- **의존성 확인**: 시작하려는 작업의 선행 조건이 충족되었는지 확인

## 4. 기능 계획서 작성

**참조 문서**:
- `docs/templates/SKILL.md` - 계획서 작성 가이드 (TDD, Quality Gate, Phase 구조)
- `docs/templates/plan-template.md` - 계획서 템플릿

**작성 위치**: `docs/plans/PLAN_[기능명].md`

**필수 섹션**:
- Overview (Feature Description, Success Criteria)
- Architecture Decisions ← **디자인 문서에서 결정한 내용 반영**
- Dependencies
- Test Strategy
- Implementation Phases (각 Phase별 Tasks, Quality Gate)
- Risk Assessment
- Progress Tracking

**통합 계획서 업데이트**:
- `PLAN_master.md`의 계획서 목록에 추가
- 의존성 그래프에 추가
- 마일스톤에 연결 (해당 시)

## 5. 기능 계획서 기반으로 구현

각 Phase별로 순차 진행:

1. **RED Phase**: 테스트 먼저 작성 (실패하는 테스트)
2. **GREEN Phase**: 테스트 통과하는 최소 코드 작성
3. **REFACTOR Phase**: 코드 품질 개선

**Phase 완료 시 Quality Gate 확인**:

// turbo
```bash
poetry run ruff check src/
```

// turbo
```bash
poetry run pytest tests/ -v --tb=short
```

**체크리스트**:
- [ ] **계획서 정합성 검토**: 구현 결과가 계획서의 내용(설계, 요구사항)과 정확히 일치하는지 확인
- [ ] 모든 Task 체크박스 완료
- [ ] Quality Gate 모든 항목 통과
- [ ] 계획서 "Last Updated" 날짜 업데이트
- [ ] Phase 상태를 ✅ Complete로 변경

## 6. CI 사전 검증 (모든 Phase 완료 후)

모든 페이즈가 완료되면, PR 생성 전 로컬 환경에서 CI 요구사항을 충족하는지 최종 확인합니다.

// turbo
```bash
# CI 설정 확인 (lint, test 등 스텝 확인)
cat .github/workflows/ci.yml
```

**수동 검증 실행**: 위 파일에 정의된 스크립트(pytest, ruff 등)를 로컬에서 모두 실행하여 에러가 없는지 확인합니다.

## 7. Git 커밋 및 푸시

반복적인 커밋과 푸시를 통해 작업을 저장합니다.

**커밋**:
```bash
# 변경된 파일 확인
git status

# 의도한 파일만 명시적으로 지정하여 스테이징 (전체 추가 지양)
git add [파일경로1] [파일경로2]
# 예: git add src/main.py tests/test_main.py

git commit -m "feat: [계획서ID] [변경 내용 요약]

- 변경사항 1
- 변경사항 2

[계획서ID]: [상태]"
```

**푸시**:
```bash
git push -u origin feat/[계획서ID]-[기능명]
```

## 8. PR 생성

**PR 제목 형식**:
```
feat: [계획서ID] [기능 요약]
# 예: feat: P-013 외부 캘린더 연동 (Google/iCloud)
```

**PR 템플릿** (`.github/pull_request_template.md`):

```markdown
## 📋 변경 사항
- 변경사항 1
- 변경사항 2

## 🎯 관련 이슈
- 계획서 ID 및 설명

## 🧪 테스트 방법
1. poetry run pytest tests/
2. 결과 확인

## ✅ 체크리스트
- [ ] 코드가 정상적으로 동작함
- [ ] 테스트를 추가/수정함 (해당하는 경우)
- [ ] 문서를 업데이트함 (해당하는 경우)
- [ ] CI 테스트 통과 확인

## 💬 추가 메모
추가 정보
```

## 9. 머지 후 정리

- **통합 계획서 업데이트**: 진행률, 상태 변경
- **main 브랜치 동기화**:
```bash
git checkout main
git pull origin main
```
- **로컬 브랜치 삭제**:
```bash
git branch -d feat/[계획서ID]-[기능명]
```
