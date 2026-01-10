# SPEC-000: CI/CD & Development Workflow

**Version**: 1.0
**Date**: 2026-01-08
**Status**: DRAFT
**References**: SRS-001 (Foundational Setup)

---

## 1. Introduction
본 문서는 안전하고 효율적인 협업을 위한 GitHub Workflow 전략 및 Branch 정책을 정의합니다.

---

## 2. Branch Strategy

### 2.1 Branch Types (Standard Prefixes)
*   **`main`**: 배포 가능한 상태(Production Ready). 직접 Push 불가.
*   **`feature/*`**: 새로운 기능 개발 (예: `feature/login`).
*   **`fix/*`**: 버그 수정 (예: `fix/parsing-error`).
*   **`refactor/*`**: 기능 변경 없는 코드 구조 개선 (예: `refactor/auth-service`).
*   **`chore/*`**: 빌드, 설정, 패키지 매니저 등 유지보수 (예: `chore/update-poetry`).
*   **`docs/*`**: 문서(Specs, Readme) 변경 (예: `docs/update-api-spec`).
*   **`test/*`**: 테스트 코드 추가/수정 (예: `test/add-user-model`).
*   **`hotfix/*`**: 프로덕션 긴급 수정.

### 2.2 Lifecycle
1.  Developer는 `main`에서 `feature/xxx` 브랜치를 생성.
2.  작업 완료 후 `main`으로 Pull Request(PR) 생성.
3.  CI Test(`pytest`, `lint`) 통과 필수.
4.  Reviewer 승인 또는 CI 통과 확인 후 Merge.
5.  **Merge 완료 시 원격 브랜치(`feature/xxx`) 자동 삭제.**

---

## 3. GitHub Actions Workflow

### 3.1 Trigger Rules & Optimization
*   **Push**: `main`, `feature/*`, `fix/*`, `refactor/*`, `hotfix/*` 브랜치.
*   **Pull Request**: `main` 브랜치 대상.
*   **Optimization (Skip Tests)**:
    *   `docs/*` 브랜치는 CI Trigger에서 제외하거나 Lint만 수행.
    *   **Paths Ignore**: `docs/**`, `*.md` 파일만 변경된 경우 Test Job 생략.

### 3.2 Jobs Definition
#### Job 1: Test & Lint
*   **Environment**: `ubuntu-latest`
*   **Condition**: `docs/**` 외의 코드 변경이 있을 때만 실행.
*   **Steps**:
    1.  Checkout Code
    2.  Set up Python 3.11
    3.  Install Dependencies (Poetry)
    4.  Run Linter (`ruff`)
    5.  Run Tests (`pytest`)
*   **Condition**: 이 Job이 성공해야만 Merge 가능 (GitHub Branch Protection Rule 설정 필요).

---

## 4. Implementation Checklist
- [ ] `.github/workflows/ci.yml` 작성
- [ ] GitHub Repository Settings -> Branch Protection Rule 설정 (`main`)
    - [ ] `Require status checks to pass before merging` 체크
- [ ] Repository Settings -> General -> `Automatically delete head branches` 체크

---
