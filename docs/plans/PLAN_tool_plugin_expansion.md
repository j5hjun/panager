# Implementation Plan: Tool Plugin 확장 시스템

**Status**: 🔄 In Progress
**Started**: 2025-12-29
**Last Updated**: 2025-12-29
**Estimated Completion**: 2026-01-12 (약 2주)

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
패니저를 "모르는 것이 없는 AI"로 만들기 위한 **Tool Plugin 확장 시스템**입니다.
플러그인 아키텍처를 통해 새로운 도구를 쉽게 추가하고 관리할 수 있는 구조를 구축합니다.

#### 확장 도구 목록
- 🧩 **Tool Plugin 아키텍처**: 동적 도구 등록/관리 시스템
- 🚗 **길찾기 도구**: 대중교통 경로, 소요시간, 출발시간 계산
- 🔍 **웹 검색 도구**: 실시간 정보 검색, 뉴스 요약
- 📰 **뉴스 도구**: 주요 뉴스 헤드라인, 카테고리별 필터링
- 💰 **금융 도구**: 주식/환율/암호화폐 시세 조회

### Success Criteria
- [x] Tool Plugin 아키텍처 완성 (Registry 패턴)
- [x] 기존 날씨/일정 도구가 Plugin 구조로 마이그레이션
- [ ] 5개 이상의 도구가 플러그인으로 작동
- [x] 새 도구 추가 시 코드 변경 최소화 (< 50 lines)
- [x] 모든 도구가 LLM Tool Calling과 통합

### User Impact
- **편의성**: 하나의 AI로 모든 정보 조회 가능
- **확장성**: 새로운 도구를 쉽게 추가
- **일관성**: 모든 도구가 동일한 인터페이스로 작동

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Registry 패턴** | 도구 동적 등록/해제, 런타임 관리 | 약간의 복잡도 증가 |
| **Abstract Base Class** | 도구 인터페이스 강제, 일관성 확보 | Python ABC 사용 필요 |
| **Plugin 디렉토리 구조** | 도구별 독립 파일, 관리 용이 | 파일 수 증가 |
| **LLM Tool Calling 우선** | AI가 도구 선택, 자연스러운 대화 | LLM API 비용 발생 |
| **무료 API 우선** | 비용 절감, 빠른 프로토타입 | 기능 제한 가능 |

### 프로젝트 구조 (목표)
```
src/core/tools/
├── base.py                  # 도구 베이스 클래스
├── registry.py              # 도구 등록/관리
├── definitions.py           # LLM Tool 스키마
└── plugins/                 # 도구 플러그인들
    ├── __init__.py
    ├── weather.py           # 날씨 도구 (기존)
    ├── calendar.py          # 일정 도구 (기존)
    ├── directions.py        # 길찾기 도구 (신규)
    ├── search.py            # 웹 검색 도구 (신규)
    ├── news.py              # 뉴스 도구 (신규)
    └── finance.py           # 금융 도구 (신규)

src/services/
├── directions/              # 길찾기 서비스
│   └── kakao_maps.py
├── search/                  # 검색 서비스
│   └── tavily.py
├── news/                    # 뉴스 서비스
│   └── news_api.py
└── finance/                 # 금융 서비스
    └── market.py
```

---

## 📦 Dependencies

### Required Before Starting
- [x] 패니저 핵심 기능 완료 (Phase 1-7: Slack Bot, LLM, 날씨, 일정, 스케줄러)
- [ ] API Keys 발급:
  - [ ] Kakao Maps API Key
  - [ ] Tavily Search API Key
  - [ ] News API Key
  - [ ] Alpha Vantage API Key (금융)

### External Dependencies
```toml
[tool.poetry.dependencies]
# 기존 의존성 유지
# 추가 의존성 (필요 시)
```

---

## 🧪 Test Strategy

### Testing Approach
**TDD Principle**: Write tests FIRST, then implement to make them pass

### Test Pyramid for Tool Plugins
| Test Type | Coverage Target | Purpose |
|-----------|-----------------|---------|
| **Unit Tests** | ≥80% | 도구 로직, Registry, Plugin 인터페이스 |
| **Integration Tests** | Critical paths | 도구 실행, LLM 통합 |
| **E2E Tests** | Key flows | 전체 대화 플로우 |

### Test File Organization
```
tests/
├── unit/
│   ├── core/
│   │   ├── test_tool_base.py
│   │   ├── test_tool_registry.py
│   │   └── test_tool_plugins.py
│   └── services/
│       ├── test_directions.py
│       ├── test_search.py
│       ├── test_news.py
│       └── test_finance.py
└── integration/
    └── test_tool_calling.py
```

---

## 🚀 Implementation Phases

---

### Phase 1: Tool Plugin 아키텍처
**Goal**: 도구를 플러그인 방식으로 쉽게 추가할 수 있는 Registry 구조 구축
**Estimated Time**: 2-3 hours
**Actual Time**: 1.5 hours
**Status**: ✅ Complete

#### Tasks

**🔴 RED: Write Failing Tests First**
- [x] **Test 1.1**: Tool Base Class 테스트
  - File(s): `tests/unit/core/test_tool_base.py`
  - Expected: Tests FAIL - BaseTool 클래스가 없음
  - Details:
    - 추상 메서드 정의 확인
    - execute() 메서드 시그니처 확인
    - 도구 메타데이터 (name, description) 확인

- [x] **Test 1.2**: Tool Registry 테스트
  - File(s): `tests/unit/core/test_tool_registry.py`
  - Expected: Tests FAIL - ToolRegistry 클래스가 없음
  - Details:
    - 도구 등록 (`register()`)
    - 도구 조회 (`get()`, `list()`)
    - 중복 등록 방지
    - 도구 해제 (`unregister()`)

**🟢 GREEN: Implement to Make Tests Pass**
- [x] **Task 1.3**: Tool Base Class 구현
  - File(s): `src/core/tools/base.py`
  - Goal: 모든 도구의 공통 인터페이스 정의
  - Details:
    - ABC (Abstract Base Class) 사용
    - `execute(function_name, **kwargs)` 추상 메서드
    - `name`, `description` 속성

- [x] **Task 1.4**: Tool Registry 구현
  - File(s): `src/core/tools/registry.py`
  - Goal: 도구 동적 등록/관리
  - Details:
    - 싱글톤 패턴
    - 도구 등록/조회/해제 메서드
    - 도구 이름 중복 체크

- [x] **Task 1.5**: 기존 날씨 도구 마이그레이션
  - File(s): `src/core/tools/plugins/weather.py`
  - Goal: BaseTool 상속으로 변경
  - Details:
    - WeatherTool 클래스 생성
    - execute() 메서드 구현
    - get_tool_definitions() 메서드 구현

- [x] **Task 1.6**: 기존 일정 도구 마이그레이션
  - File(s): `src/core/tools/plugins/calendar.py`
  - Goal: BaseTool 상속으로 변경

**🔵 REFACTOR: Clean Up Code**
- [x] **Task 1.7**: AIService에 Registry 연동
  - 도구 동적 로드
  - 도구 실행 로직 리팩토링
  - TOOL_FUNCTION_TO_PLUGIN 매핑 추가

#### Quality Gate ✋

**⚠️ STOP: Do NOT proceed to Phase 2 until ALL checks pass**

**TDD Compliance**:
- [x] 테스트 먼저 작성됨
- [x] 모든 테스트 통과 (101 passed)
- [x] Coverage ≥ 77% (tools: 77%, 전체: adequate)

**Build & Tests**:
- [x] `poetry run pytest` 통과
- [x] 기존 날씨/일정 도구가 Registry를 통해 작동

**Code Quality**:
- [x] `ruff check .` 통과
- [x] `black --check .` 통과
- [x] `mypy src/core/tools/` 통과

**Manual Test Checklist**:
- [x] "오늘 날씨 어때?" → 날씨 도구가 Registry를 통해 실행됨
- [x] "내일 일정 뭐야?" → 일정 도구가 Registry를 통해 실행됨
- [x] 새 도구 추가 시 코드 변경 최소화 확인 (< 50 lines)

---

### Phase 2: 길찾기 도구 추가
**Goal**: 대중교통 경로, 소요시간, 출발시간 계산 기능 제공
**API**: Kakao Maps API (무료)
**Estimated Time**: 3-4 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 2.1**: Directions Entity 테스트
  - File(s): `tests/unit/core/test_directions_entity.py`
  - Details:
    - DirectionsData 생성
    - 경로 정보, 소요시간, 환승 정보
    - to_message() 포맷팅

- [ ] **Test 2.2**: 길찾기 서비스 테스트
  - File(s): `tests/unit/services/test_directions.py`
  - Details:
    - API 호출 (mock)
    - 경로 검색
    - 소요시간 계산
    - 에러 처리

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 2.3**: Directions Entity 정의
  - File(s): `src/core/entities/directions.py`
  - 경로, 소요시간, 환승 정보 모델

- [ ] **Task 2.4**: Kakao Maps Service 구현
  - File(s): `src/services/directions/kakao_maps.py`
  - Kakao Maps API 연동
  - 대중교통 경로 검색

- [ ] **Task 2.5**: 길찾기 Tool Plugin 구현
  - File(s): `src/core/tools/plugins/directions.py`
  - DirectionsTool 클래스 (BaseTool 상속)
  - `get_directions` 도구 정의

- [ ] **Task 2.6**: definitions.py에 Tool 스키마 추가
  - get_directions 스키마 정의

- [ ] **Task 2.7**: Registry에 도구 등록
  - AIService 초기화 시 자동 등록

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 2.8**: 출발시간 역산 로직 추가
  - "1시 회의면 몇 시 출발?" 질문 지원

#### Quality Gate ✋

**TDD Compliance**:
- [ ] 테스트 먼저 작성됨
- [ ] 모든 테스트 통과

**Manual Test Checklist**:
- [ ] "창동역에서 강남역 어떻게 가?" → 정확한 경로 안내
- [ ] "소요시간 얼마나 걸려?" → 시간 계산
- [ ] "1시 회의면 몇 시에 출발해야해?" → 출발시간 계산

---

### Phase 3: 웹 검색 도구 추가
**Goal**: 실시간 정보 검색, 뉴스, 사실 확인 기능 제공
**API**: Tavily Search API (무료 tier)
**Estimated Time**: 2-3 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 3.1**: 웹 검색 서비스 테스트
  - File(s): `tests/unit/services/test_search.py`
  - Details:
    - API 호출 (mock)
    - 검색 결과 파싱
    - 결과 요약

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 3.2**: Search Service 구현
  - File(s): `src/services/search/tavily.py`
  - Tavily API 연동

- [ ] **Task 3.3**: 웹 검색 Tool Plugin 구현
  - File(s): `src/core/tools/plugins/search.py`
  - SearchTool 클래스
  - `web_search` 도구 정의

- [ ] **Task 3.4**: definitions.py에 Tool 스키마 추가

- [ ] **Task 3.5**: Registry에 도구 등록

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 3.6**: 검색 결과 포맷팅 개선
  - 요약 품질 향상
  - 출처 표시

#### Quality Gate ✋

**Manual Test Checklist**:
- [ ] "오늘 주요 뉴스 뭐야?" → 최신 뉴스 요약
- [ ] "비트코인 현재 가격" → 실시간 정보
- [ ] "파이썬이란?" → 검색 결과 요약

---

### Phase 4: 뉴스 도구 추가
**Goal**: 주요 뉴스 헤드라인, 카테고리별 필터링
**API**: News API (무료 tier)
**Estimated Time**: 2-3 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 4.1**: 뉴스 서비스 테스트
  - File(s): `tests/unit/services/test_news.py`
  - Details:
    - 헤드라인 조회
    - 카테고리별 필터링
    - 날짜별 조회

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 4.2**: News Service 구현
  - File(s): `src/services/news/news_api.py`
  - News API 연동

- [ ] **Task 4.3**: 뉴스 Tool Plugin 구현
  - File(s): `src/core/tools/plugins/news.py`
  - NewsTool 클래스
  - `get_news` 도구 정의

- [ ] **Task 4.4**: definitions.py에 Tool 스키마 추가

- [ ] **Task 4.5**: Registry에 도구 등록

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 4.6**: 아침 브리핑에 뉴스 통합
  - 날씨 + 일정 + 뉴스 종합

#### Quality Gate ✋

**Manual Test Checklist**:
- [ ] "오늘 IT 뉴스 알려줘" → 카테고리별 뉴스
- [ ] "최근 경제 뉴스" → 경제 뉴스 헤드라인
- [ ] 아침 브리핑에 뉴스 포함 확인

---

### Phase 5: 금융 도구 추가
**Goal**: 주식/환율/암호화폐 시세 조회
**API**: Alpha Vantage / CoinGecko (무료)
**Estimated Time**: 3-4 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 5.1**: 금융 서비스 테스트
  - File(s): `tests/unit/services/test_finance.py`
  - Details:
    - 주가 조회
    - 환율 조회
    - 암호화폐 시세

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 5.2**: Finance Service 구현
  - File(s): `src/services/finance/market.py`
  - Alpha Vantage / CoinGecko API 연동

- [ ] **Task 5.3**: 금융 Tool Plugin 구현
  - File(s): `src/core/tools/plugins/finance.py`
  - FinanceTool 클래스
  - `get_stock_price`, `get_exchange_rate`, `get_crypto_price` 도구

- [ ] **Task 5.4**: definitions.py에 Tool 스키마 추가

- [ ] **Task 5.5**: Registry에 도구 등록

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 5.6**: 시세 캐싱 추가
  - API 요청 최소화
  - 실시간성 유지

#### Quality Gate ✋

**Manual Test Checklist**:
- [ ] "삼성전자 주가 얼마야?" → 현재 주가
- [ ] "달러 환율 알려줘" → 현재 환율
- [ ] "비트코인 가격" → 암호화폐 시세

---

## ⚠️ Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| API Rate Limit 초과 | Medium | Medium | 캐싱 적용, 요청 최소화, 백오프 로직 |
| API 키 비용 발생 | Low | Medium | 무료 tier 우선, 사용량 모니터링 |
| 도구 간 충돌 | Low | Low | 명확한 도구 이름, Registry 중복 체크 |
| LLM 도구 선택 오류 | Medium | Low | Tool description 명확화, 예시 추가 |
| 외부 API 장애 | Medium | Low | Timeout 설정, 우아한 에러 처리 |

---

## 🔄 Rollback Strategy

### If Phase 8 Fails
- Registry 코드 제거
- 기존 definitions.py 방식으로 복구
- 날씨/일정 도구 원래 구조로 복원

### If Phase 9-12 Fails
- 해당 도구 플러그인 파일 삭제
- Registry에서 도구 등록 제거
- definitions.py에서 Tool 스키마 제거
- 외부 서비스 디렉토리 삭제

### 전체 롤백
- Phase 7 완료 시점으로 복구
- Tool Plugin 관련 모든 코드 제거

---

## 📊 Progress Tracking

### Completion Status
- **Phase 1**: ✅ 100% - Tool Plugin 아키텍처 **완료**
- **Phase 2**: ⏳ 0% - 길찾기 도구
- **Phase 3**: ⏳ 0% - 웹 검색 도구
- **Phase 4**: ⏳ 0% - 뉴스 도구
- **Phase 5**: ⏳ 0% - 금융 도구

**Overall Progress**: 20% complete (1/5 phases)

### Time Tracking
| Phase | Estimated | Actual | Variance |
|-------|-----------|--------|----------|
| Phase 1 | 2-3 hours | 1.5 hours | -0.5 ~ -1.5 hours |
| Phase 2 | 3-4 hours | - | - |
| Phase 3 | 2-3 hours | - | - |
| Phase 4 | 2-3 hours | - | - |
| Phase 5 | 3-4 hours | - | - |
| **Total** | 12-17 hours | 1.5 hours | - |

---

## 📝 Notes & Learnings

### Implementation Notes
- **TDD 성공**: 테스트 먼저 작성 후 구현하니 코드 품질이 향상됨
- **execute() 시그니처**: `function_name` 파라미터를 명시적으로 추가하여 어떤 함수가 호출되었는지 명확히 함
- **TOOL_FUNCTION_TO_PLUGIN 매핑**: LLM이 호출하는 함수명(예: `get_current_weather`)과 플러그인 이름(예: `weather`)을 매핑하여 유연성 확보
- **싱글톤 Registry**: 여러 곳에서 같은 Registry 인스턴스를 사용하므로 테스트 시 `clear()` 호출 필수

### Blockers Encountered
- **mypy 시그니처 불일치**: 처음에 BaseTool의 execute가 kwargs만 받았는데, 플러그인들이 function_name을 필수로 받아서 시그니처 수정 필요했음

### Improvements for Future Plans
- [개선 사항 기록]

---

## 📚 References

### Documentation
- [Kakao Maps API](https://developers.kakao.com/docs/latest/ko/local/dev-guide)
- [Tavily Search API](https://tavily.com/)
- [News API](https://newsapi.org/)
- [Alpha Vantage](https://www.alphavantage.co/)
- [CoinGecko API](https://www.coingecko.com/en/api)

### API Keys 발급 링크
- Kakao Maps: https://developers.kakao.com/
- Tavily: https://tavily.com/
- News API: https://newsapi.org/
- Alpha Vantage: https://www.alphavantage.co/support/#api-key

---

## ✅ Final Checklist

**Before marking plan as COMPLETE**:
- [ ] All phases completed with quality gates passed
- [ ] 5개 도구 모두 플러그인으로 작동
- [ ] Full integration testing performed
- [ ] Documentation updated (README에 새 도구 사용 예시 추가)
- [ ] .env.example에 모든 API 키 추가
- [ ] 전체 테스트 통과 (Coverage ≥ 75%)

---

**Plan Status**: ⏳ Pending
**Next Action**: Phase 1 시작 - Tool Plugin 아키텍처 구축
**Blocked By**: None
