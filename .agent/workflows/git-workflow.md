---
description: Git 브랜치 전략 및 코드 푸시 워크플로우
---

# Git 워크플로우 가이드

이 프로젝트는 **Feature Branch + PR 기반 워크플로우**를 사용합니다.
main 브랜치에 직접 푸시하는 것은 금지되어 있습니다.

---

## 🌿 새 기능 개발 시

// turbo-all

### 1. 최신 main 브랜치로 이동
```bash
git checkout main
git pull origin main
```

### 2. Feature 브랜치 생성
```bash
git checkout -b feature/기능이름
```

**브랜치 네이밍 규칙:**
- `feature/` - 새 기능 (예: `feature/calendar-tool`)
- `fix/` - 버그 수정 (예: `fix/api-timeout`)
- `refactor/` - 리팩토링 (예: `refactor/tool-registry`)
- `docs/` - 문서 작업 (예: `docs/readme-update`)
- `hotfix/` - 긴급 수정 (예: `hotfix/critical-bug`)
- `chore/` - 유지보수 (예: `chore/update-deps`)

### 3. 작업 및 커밋
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

**커밋 메시지 규칙:**
- `feat:` 새 기능
- `fix:` 버그 수정
- `docs:` 문서 변경
- `style:` 포맷팅 (코드 변경 X)
- `refactor:` 리팩토링
- `test:` 테스트 추가/수정
- `chore:` 빌드, 패키지 등 유지보수

### 4. 원격에 푸시
```bash
git push -u origin feat/[계획서ID]-[기능명]
```

### 5. PR (Pull Request) 생성
1. GitHub 저장소 페이지 접속
2. "Compare & pull request" 버튼 클릭
3. PR 제목 및 설명 작성
4. "Create pull request" 클릭

### 6. CI 통과 확인
- PR 페이지에서 CI 체크 통과 확인
- 모든 체크가 녹색 ✅ 인지 확인

### 7. PR 머지
- "Squash and merge" 클릭
- (선택) 커밋 메시지 수정
- "Confirm squash and merge" 클릭

### 8. 로컬 정리
```bash
git checkout main
git pull origin main
git branch -d feature/기능이름
```

---

## 🔥 긴급 수정 (Hotfix) 시

동일한 워크플로우를 따르되, `hotfix/` 접두사를 사용합니다:

```bash
git checkout main
git pull origin main
git checkout -b hotfix/긴급수정내용
# 수정 작업
git add .
git commit -m "fix: 긴급 버그 수정"
git push -u origin hotfix/긴급수정내용
# GitHub에서 PR 생성 → 빠르게 리뷰 → 머지
```

---

## ⚠️ 주의사항

1. **main에 직접 푸시 금지**: Branch Protection이 설정되어 있어 거부됩니다.
2. **CI 통과 필수**: 테스트 실패 시 머지할 수 없습니다.
3. **브랜치 삭제 자동화**: 머지 후 원격 브랜치는 자동 삭제됩니다.
4. **로컬 브랜치 정리**: 머지 후 로컬 브랜치는 수동으로 삭제해주세요.

---

## 📋 자주 사용하는 명령어

```bash
# 현재 브랜치 확인
git branch

# 모든 브랜치 확인 (원격 포함)
git branch -a

# 브랜치 삭제 (로컬)
git branch -d 브랜치이름

# 강제 삭제 (머지되지 않은 브랜치)
git branch -D 브랜치이름

# 원격 브랜치 동기화
git fetch --prune

# 최근 커밋 로그 확인
git log --oneline -10
```

---

## 🔗 관련 문서

- [계획서](../docs/plans/PLAN_git_workflow_improvement.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)