---
description: 새 기능 개발 시 따라야 할 전체 워크플로우 (요구사항 → 계획 → 구현 → PR)
---

# 기능 개발 워크플로우

새로운 기능을 개발할 때 따라야 할 전체 프로세스입니다.

## 1. 요구사항 정의서 확인/작성

기능 개발 전 요구사항이 정의되어 있는지 확인합니다.

- **기존 SRS 확인**: `docs/SRS_*.md` 파일에 해당 기능의 요구사항이 있는지 확인
- **신규 작성 필요 시**: IEEE 830 표준 기반으로 SRS 작성
- **요구사항 ID 확인**: 구현할 기능의 FR-XXX 또는 NFR-XXX ID 파악

## 2. 통합 계획서 확인

// turbo
```bash
cat docs/plans/PLAN_master.md | head -150
```

- **현황 파악**: 전체 프로젝트 진행 상황 확인
- **의존성 확인**: 시작하려는 작업의 선행 조건이 충족되었는지 확인
- **계획서 ID 확인**: 다음 사용 가능한 ID 파악 (P-005, P-006, ...)

## 3. 기능 계획서 작성

**참조 문서**:
- `docs/tamplates/SKILL.md` - 계획서 작성 가이드 (TDD, Quality Gate, Phase 구조)
- `docs/tamplates/plan-template.md` - 계획서 템플릿

**작성 위치**: `docs/plans/PLAN_[기능명].md`

**필수 섹션**:
- Overview (Feature Description, Success Criteria)
- Architecture Decisions
- Dependencies
- Test Strategy
- Implementation Phases (각 Phase별 Tasks, Quality Gate)
- Risk Assessment
- Progress Tracking

**통합 계획서 업데이트**:
- `PLAN_master.md`의 계획서 목록에 추가
- 의존성 그래프에 추가
- 마일스톤에 연결 (해당 시)

## 4. 기능 계획서 기반으로 구현

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
- [ ] 모든 Task 체크박스 완료
- [ ] Quality Gate 모든 항목 통과
- [ ] 계획서 "Last Updated" 날짜 업데이트
- [ ] Phase 상태를 ✅ Complete로 변경

## 5. Git 워크플로우

**브랜치 생성**:
```bash
git checkout -b feat/[계획서ID]-[기능명]
# 예: git checkout -b feat/p-010-autonomous-core
```

**커밋**:
```bash
git add -A
git commit -m "feat: [계획서ID] [변경 내용 요약]

- 변경사항 1
- 변경사항 2

[계획서ID]: [상태]"
```

**푸시**:
```bash
git push -u origin feat/[계획서ID]-[기능명]
```

## 6. PR 생성

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

## 7. 머지 후 정리

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
