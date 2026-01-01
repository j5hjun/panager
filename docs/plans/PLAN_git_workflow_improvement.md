# Implementation Plan: Git 워크플로우 개선

**Status**: ✅ Complete
**Started**: 2025-12-29
**Last Updated**: 2026-01-01
**Completed**: 2026-01-01

---

**⚠️ CRITICAL INSTRUCTIONS**: After completing each phase:
1. ✅ Check off completed task checkboxes
2. 🧪 Run all quality gate validation commands
3. ⚠️ Verify ALL quality gate items pass
4. 📅 Update "Last Updated" date above
5. 📝 Document learnings in Notes section
6. ➡️ Only then proceed to next phase

⛔ **DO NOT skip quality gates or proceed with failing checks**

---

## 📋 Overview

### Feature Description
1인 개발 환경에서도 안전하고 체계적인 코드 관리를 위한 **Git 워크플로우 개선**입니다.
Feature Branch + PR 기반 워크플로우를 도입하여 main 브랜치를 항상 안정적인 상태로 유지하고,
실수로 인한 버그가 프로덕션에 바로 배포되는 위험을 방지합니다.

#### 주요 개선 사항
- 🌿 **Feature Branch 전략**: main 직접 푸시 금지, PR 필수
- 🔒 **Branch Protection Rules**: GitHub 설정을 통한 브랜치 보호
- ✅ **CI 연동 강화**: PR에서 CI 통과 필수
- 📝 **Commit Convention**: 일관된 커밋 메시지 규칙
- 📖 **워크플로우 문서화**: 팀 확장 대비 문서화

### Success Criteria
- [x] main 브랜치에 직접 푸시 불가 설정
- [x] PR 생성 시 CI 자동 실행
- [x] CI 통과 후에만 머지 가능
- [x] 워크플로우 문서 작성 완료
- [x] 개발자가 새 워크플로우로 코드 푸시 성공

### User Impact
- **안정성**: main 브랜치가 항상 배포 가능한 상태 유지
- **추적성**: PR 단위로 변경 이력 관리
- **확장성**: 향후 팀 확장 시 협업 용이
- **안전성**: 실수로 인한 버그 배포 방지

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Feature Branch 전략** | 간단하면서도 안전한 워크플로우 | 약간의 추가 단계 필요 |
| **PR 필수화** | 코드 리뷰 습관, CI 통과 보장 | 1인 개발 시 셀프 리뷰 |
| **Squash Merge** | 깔끔한 커밋 히스토리 | 상세 히스토리 손실 |
| **Conventional Commits** | 일관된 커밋 메시지, 자동 changelog 가능 | 학습 비용 |
| **Branch 자동 삭제** | 브랜치 정리 자동화 | 없음 |

### 워크플로우 다이어그램
```
main (프로덕션) ← PR (Squash Merge) ← feature/xxx (개발)
     │                                      │
     ├── 항상 CI 통과된 안정적인 상태         │
     │                                      │
     └── deploy.yml → 배포                 └── 자유롭게 커밋
```

### 브랜치 네이밍 컨벤션
```
feature/  - 새 기능 (예: feature/calendar-tool)
fix/      - 버그 수정 (예: fix/api-timeout)
refactor/ - 리팩토링 (예: refactor/tool-registry)
docs/     - 문서 작업 (예: docs/readme-update)
hotfix/   - 긴급 수정 (예: hotfix/critical-bug)
chore/    - 유지보수 (예: chore/update-deps)
```

### Conventional Commits 규칙
```
feat:     새 기능
fix:      버그 수정
docs:     문서 변경
style:    포맷팅, 세미콜론 등 (코드 변경 X)
refactor: 리팩토링
test:     테스트 추가/수정
chore:    빌드, 패키지 등 유지보수
```

---

## 📦 Dependencies

### Required Before Starting
- [x] GitHub 저장소 Admin 권한
- [x] CI/CD 워크플로우 설정 완료 (ci.yml, deploy.yml)
- [x] GitHub Branch Protection Rules 설정 가능 여부 확인

### External Dependencies
- GitHub Branch Protection Rules (무료 플랜에서 public repo만 가능)
- (Optional) pre-commit 훅을 위한 husky 또는 pre-commit 패키지

---

## 🧪 Test Strategy

### Testing Approach
각 Phase 완료 후 실제 워크플로우를 테스트하여 검증합니다.

### Test Scenarios
| Test | Description | Expected Result |
|------|-------------|-----------------|
| **main 직접 푸시** | main에 직접 push 시도 | 거부됨 |
| **PR 없이 머지** | PR 생성 없이 머지 시도 | 불가능 |
| **CI 실패 후 머지** | CI 실패 상태에서 머지 시도 | 거부됨 |
| **정상 워크플로우** | feature branch → PR → CI 통과 → 머지 | 성공 |

---

## 🚀 Implementation Phases

---

### Phase 1: GitHub Branch Protection 설정
**Goal**: main 브랜치를 보호하여 직접 푸시 방지, PR 필수화
**Estimated Time**: 30분
**Actual Time**: 15분
**Status**: ✅ Complete

#### Tasks

- [x] **Task 1.1**: GitHub Repository Settings 접근
  - GitHub 저장소 → Settings → Branches
  - "Add branch protection rule" 클릭

- [x] **Task 1.2**: Branch Protection Rule 설정
  - **Branch name pattern**: `main`
  - 설정 항목:
    - [x] ✅ Require a pull request before merging
      - [x] Require approvals: 0 (1인 개발이므로)
    - [x] ✅ Require status checks to pass before merging
      - [x] ✅ Require branches to be up to date before merging
      - [x] Status checks: `test` (ci.yml의 job 이름)
    - [x] ❌ Require signed commits (선택사항 - 스킵)
    - [x] ✅ Do not allow bypassing the above settings

- [x] **Task 1.3**: 설정 저장 및 확인
  - "Create" 또는 "Save changes" 클릭
  - Rule이 적용되었는지 확인

#### Quality Gate ✋

**⚠️ STOP: Do NOT proceed to Phase 2 until ALL checks pass**

**Verification**:
- [x] `git push origin main` 시도 → 거부됨 확인
  - `GH006: Protected branch update failed`
  - `Changes must be made through a pull request`
  - `Required status check "test" is expected`
- [x] GitHub에서 Branch Protection Rule 활성화 확인
- [x] Required status check에 `test` 표시됨

---

### Phase 2: PR 템플릿 및 자동화 설정
**Goal**: PR 생성 시 일관된 형식, 머지 후 브랜치 자동 삭제
**Estimated Time**: 20분
**Actual Time**: 5분
**Status**: ✅ Complete

#### Tasks

- [x] **Task 2.1**: PR 템플릿 생성
  - File: `.github/pull_request_template.md`
  - 내용: 변경 사항, 체크리스트 등

- [x] **Task 2.2**: GitHub 설정 - 자동 브랜치 삭제
  - Settings → General → Pull Requests
  - ✅ "Automatically delete head branches" 활성화

- [x] **Task 2.3**: Default merge method 설정
  - Settings → General → Pull Requests
  - ✅ "Allow squash merging" (유일하게 허용)
  - Squash merge만 허용하여 깔끔한 히스토리 유지

#### Quality Gate ✋

**Verification**:
- [x] PR 템플릿 파일 존재 확인
- [ ] 새 PR 생성 시 템플릿 자동 로드됨 (Phase 4에서 확인)
- [ ] 테스트 PR 머지 후 브랜치 자동 삭제됨 (Phase 4에서 확인)

---

### Phase 3: 워크플로우 문서 작성
**Goal**: 개발 워크플로우를 문서화하여 일관된 개발 프로세스 유지
**Estimated Time**: 30분
**Actual Time**: 10분
**Status**: ✅ Complete

#### Tasks

- [x] **Task 3.1**: Git 워크플로우 가이드 작성
  - File: `.agent/workflows/git-workflow.md`
  - 내용: 일상적인 개발 흐름 단계별 설명

- [x] **Task 3.2**: CONTRIBUTING.md 작성
  - File: `CONTRIBUTING.md`
  - 내용: 브랜치 네이밍, 커밋 규칙, PR 가이드

- [x] **Task 3.3**: README에 워크플로우 섹션 추가
  - 기존 README.md에 개발 가이드 링크 추가

#### Quality Gate ✋

**Verification**:
- [x] 워크플로우 문서 파일 존재 확인
- [x] 문서 내용 검토 (명확하고 따라하기 쉬운지)
- [x] README에서 문서 링크 작동 확인

---

### Phase 4: 실제 워크플로우 테스트
**Goal**: 새로운 워크플로우로 코드 변경을 수행하여 전체 프로세스 검증
**Estimated Time**: 40분
**Actual Time**: 60분 (추가 작업 포함)
**Status**: ✅ Complete

#### Tasks

- [x] **Task 4.1**: Feature Branch 생성 및 작업
  ```bash
  git checkout -b feature/test-workflow
  # 작은 변경 (예: README에 배지 추가)
  git add .
  git commit -m "docs: add CI badge to README"
  git push -u origin feature/test-workflow
  ```

- [x] **Task 4.2**: PR 생성 및 CI 확인
  - GitHub에서 PR 생성
  - CI 자동 실행 확인
  - CI 통과 확인
  - ⚠️ **Blocker 발생**: paths-ignore로 인해 문서만 변경 시 CI 스킵됨

- [x] **Task 4.2.1**: CI 워크플로우 수정 (Blocker 해결) ✅
  - **문제**: paths-ignore 설정으로 .md, docs/** 파일만 변경 시 CI가 스킵됨
  - **결과**: Branch Protection의 required status check test가 실행되지 않아 머지 불가
  - **해결**: Job 분리 전략 + dorny/paths-filter 적용
  - File: .github/workflows/ci.yml
  - 변경 내용:
    - check job 추가: 항상 실행, dorny/paths-filter로 코드 변경 감지
    - test job: main push 시 항상 실행, PR은 코드 변경 시에만 실행
  - Branch Protection 수정: required status check을 test에서 check으로 변경

- [x] **Task 4.2.2**: Branch Protection Rule 수정
  - GitHub Settings → Branches → main rule 편집
  - Required status check: test 제거, check 추가

- [x] **Task 4.2.3**: 배포 다운타임 최소화 (이미지 Pull 방식)
  - **문제**: 배포 서버에서 `docker compose build` 하는 동안 서비스 다운
  - **해결**: CI에서 이미지 빌드 & 레지스트리 푸시, 배포 서버에서는 Pull만
  - **기존 워크플로우 활용**: `docker-build.yml` (ghcr.io에 이미지 푸시)
  
  - **수정 필요 파일들**:
    1. `docker-compose.yml`: build → image 방식으로 변경
       ```yaml
       # Before
       services:
         panager:
           build:
             context: .
             dockerfile: Dockerfile
       
       # After
       services:
         panager:
           image: ghcr.io/j5hjun/panager:latest
       ```
    
    2. `deploy.yml`: build 대신 pull + 이미지 정리
       ```yaml
       # Before
       - docker compose down
       - docker compose up -d --build --wait
       
       # After
       - docker compose pull          # 새 이미지 다운로드 (서비스 유지)
       - docker compose up -d --wait  # 빠르게 컨테이너 교체
       - docker image prune -f        # 이전 이미지 정리
       ```
    
    3. 워크플로우 연동: `ci.yml → docker-build.yml → deploy.yml`

- [x] **Task 4.2.4**: 배포 문서 업데이트
  - **File 1**: `docs/DEPLOYMENT.md`
    - 배포 프로세스 섹션 업데이트 (이미지 Pull 방식 반영)
    - "Docker 이미지 직접 Pull" 섹션을 기본 방식으로 변경
    - CI/CD 프로세스 다이어그램 업데이트 (이미지 정리 단계 포함):
      ```
      main 브랜치 푸시
          ↓
      CI 워크플로우 (테스트 통과)
          ↓
      Docker Build 워크플로우 (이미지 빌드 & ghcr.io 푸시)
          ↓
      Deploy 워크플로우 (이미지 pull & 컨테이너 교체 & 이전 이미지 정리)
      ```
  
  - **File 2**: `docs/OPERATIONS.md`
    - "배포 및 업데이트" 섹션 업데이트 (58-82줄)
    - 자동 배포 프로세스 다이어그램 수정
    - 수동 배포 명령어 수정 (`--build` → `pull` + 이미지 정리)
      ```bash
      # Before
      docker compose down
      docker compose up -d --build
      
      # After
      docker compose pull
      docker compose up -d --wait
      docker image prune -f  # 이전 이미지 정리
      ```
    - 무중단 업데이트 섹션에 이미지 정리 추가
    - 롤백 섹션의 `--build` 명령어도 수정 (92, 96줄)
  
  - **File 3**: `README.md`
    - 빠른 시작 섹션의 Docker 명령어 수정 (53줄)
      ```bash
      # Before
      docker compose up -d --build
      
      # After  
      docker compose pull
      docker compose up -d
      # 선택: docker image prune -f  (이전 이미지 정리)
      ```

- [x] **Task 4.3**: PR 머지 및 정리
  - Squash and merge 실행
  - 브랜치 자동 삭제 확인
  - 로컬 정리:
    ```bash
    git checkout main
    git pull
    git branch -d ci/deploy-optimization
    ```

- [x] **Task 4.4**: 배포 및 문서 확인
  - docker-build.yml → 이미지 ghcr.io에 푸시 확인
  - deploy.yml → 이미지 pull 후 배포 확인
  - 다운타임 최소화 확인 (빌드 없이 pull만)
  - `docs/DEPLOYMENT.md` 내용이 실제 프로세스와 일치하는지 확인

#### Quality Gate ✋

**⚠️ STOP: Do NOT proceed until ALL checks pass**

**Final Verification**:
- [x] Feature branch에서 작업 → PR 생성 → CI 통과 → 머지 성공
- [x] 문서만 변경한 PR도 check job 통과로 머지 가능
- [x] 코드 변경 시 test job도 실행됨
- [x] 머지 후 브랜치 자동 삭제됨
- [x] main이 직접 푸시로부터 보호됨
- [x] 배포 시 다운타임 최소화됨 (이미지 pull만, 빌드 없음)

---

## ⚠️ Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| Branch Protection 미지원 | Low | High | Private repo pricing 확인, 또는 로컬 훅 사용 |
| 긴급 hotfix 지연 | Low | Medium | hotfix/ 브랜치 사용, 빠른 PR 머지 |
| CI 실패로 머지 불가 | Medium | Medium | CI 문제 우선 해결, 필요시 임시 bypass |
| 복잡한 워크플로우 | Low | Low | 문서화로 학습 비용 최소화 |
| **paths-ignore로 CI 스킵** | **High** | **Medium** | **Job 분리 (check + test)** |

---

## 🔄 Rollback Strategy

### If Branch Protection Fails
- GitHub Settings에서 Branch Protection Rule 삭제
- 기존 방식(main 직접 푸시)으로 복귀

### If Workflow is Too Complex
- 필수 설정만 유지 (PR 필수, CI 통과)
- 선택 설정 비활성화 (템플릿 등)

---

## 📊 Progress Tracking

### Completion Status
- **Phase 1**: ✅ 100% - GitHub Branch Protection 설정 **완료**
- **Phase 2**: ✅ 100% - PR 템플릿 및 자동화 **완료**
- **Phase 3**: ✅ 100% - 워크플로우 문서 작성 **완료**
- **Phase 4**: ✅ 100% - 실제 워크플로우 테스트 **완료**

**Overall Progress**: 100% complete (4/4 phases)

### Time Tracking
| Phase | Estimated | Actual | Variance |
|-------|-----------|--------|----------|
| Phase 1 | 30분 | 15분 | -15분 |
| Phase 2 | 20분 | 5분 | -15분 |
| Phase 3 | 30분 | 10분 | -20분 |
| Phase 4 | 40분 | 60분 | +20분 |
| **Total** | ~120분 | ~90분 | -30분 |

---

## 📝 Notes & Learnings

### Implementation Notes
- **Phase 1**: GitHub Branch Protection 설정 시 "Do not allow bypassing" 옵션이 중요함. 이 옵션이 없으면 admin이 규칙을 우회할 수 있음.
- main 직접 푸시 테스트 결과: `GH006: Protected branch update failed` 에러와 함께 거부됨 확인
- **Phase 2**: PR 템플릿과 자동 브랜치 삭제 설정 완료. Squash merge만 허용하도록 설정.
- **Phase 3**: Git 워크플로우 가이드와 CONTRIBUTING.md 작성 완료. README에 링크 추가.

### Blockers Encountered
- **Phase 4 - Task 4.2**: paths-ignore 설정으로 인한 CI 스킵 문제
  - **상황**: 문서(.md, docs/**)만 변경한 PR에서 CI의 test job이 스킵됨
  - **문제**: Branch Protection에서 test를 required로 설정했는데, job이 실행되지 않아 "Expected" 상태로 머지 불가
  - **해결 방안**: Job 분리 전략 + dorny/paths-filter
    - check job: 항상 실행, dorny/paths-filter로 코드 변경 감지
    - test job: main push 시 항상 실행, PR은 코드 변경 시에만
  - **상태**: ✅ 해결 완료 (PR #5 머지됨)

- **Phase 4 - 배포 다운타임**: 서버에서 빌드 시 서비스 다운
  - **상황**: `docker compose --build` 동안 서비스가 응답하지 않음
  - **해결 방안**: 이미지 Pull 방식으로 변경
    - CI에서 이미지 빌드 & ghcr.io 푸시 (docker-build.yml)
    - 배포 서버에서는 pull만 수행
  - **상태**: 🔄 진행 중

### Improvements for Future Plans
- CI 설계 시 paths-ignore와 Branch Protection의 상호작용 미리 고려 필요
- 문서 전용 변경에 대한 CI 전략 사전 수립
- 배포 시 빌드와 pull 분리 전략 적용

---

## 📚 References

### Documentation
- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

### Related Files
- `.github/workflows/ci.yml` - CI 워크플로우 (테스트, 린트)
- `.github/workflows/docker-build.yml` - Docker 이미지 빌드 & 푸시
- `.github/workflows/deploy.yml` - 배포 워크플로우

---

## ✅ Final Checklist

**Before marking plan as COMPLETE**:
- [x] All phases completed with quality gates passed
- [x] main 브랜치 보호 설정 완료
- [x] PR 기반 워크플로우 동작 확인
- [x] 워크플로우 문서화 완료
- [x] 팀원 (또는 미래의 자신)이 따라할 수 있는 가이드 존재

---

**Plan Status**: ✅ COMPLETE
**Completed**: 2026-01-01
**Total Time**: ~90분 (Phase 1-4)
