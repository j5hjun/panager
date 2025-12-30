# 🔧 운영 가이드

패니저 AI 비서의 운영 및 유지보수 방법을 안내합니다.

---

## 📊 모니터링

### 모니터링 도구 접속

| 서비스 | 포트 | URL | 용도 |
|--------|------|-----|------|
| **Uptime Kuma** | 3001 | `http://<서버IP>:3001` | 서비스 상태 모니터링, Slack 알림 |
| **Beszel** | 8090 | `http://<서버IP>:8090` | CPU/메모리/디스크 모니터링 |
| **Dozzle** | 9999 | `http://<서버IP>:9999` | 통합 로그 뷰어 |

### 알림 채널

- **Uptime Kuma**: 서비스 다운/복구 시 Slack 알림
- **LoggiFly**: 에러 로그 발생 시 Slack 알림

---

## 📝 로그 확인

### Docker 로그 확인

```bash
# 실시간 로그
docker logs -f panager

# 최근 100줄
docker logs --tail 100 panager

# 특정 시간 이후 로그
docker logs --since 1h panager
```

### Dozzle 사용 (웹 UI)

1. `http://<서버IP>:9999` 접속
2. `panager` 컨테이너 선택
3. 실시간 로그 스트리밍 확인

### 로그 로테이션 설정

```yaml
# docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"   # 파일당 최대 10MB
    max-file: "3"     # 최대 3개 파일
```

---

## 🔄 배포 및 업데이트

### 자동 배포 (CI/CD)

```
main 브랜치 푸시 → CI 통과 → 자동 배포
```

GitHub Actions 확인: https://github.com/j5hjun/panager/actions

### 수동 배포

```bash
cd ~/panager  # 또는 러너 작업 디렉토리
git pull origin main
docker compose down
docker compose up -d --build
```

### 무중단 업데이트

```bash
docker compose up -d --build --wait
```

---

## ⏪ 롤백

### 이전 버전으로 롤백

```bash
# 특정 커밋으로 롤백
git checkout <commit-hash>
docker compose up -d --build

# main으로 복원
git checkout main
docker compose up -d --build
```

### Docker 이미지 롤백

```bash
# 이전 이미지 태그 확인
docker images ghcr.io/j5hjun/panager

# 특정 버전으로 실행
docker compose down
docker pull ghcr.io/j5hjun/panager:<sha>
# docker-compose.yml에서 이미지 태그 수정 후
docker compose up -d
```

---

## 💾 백업 및 복구

### 백업 대상

| 항목 | 경로 | 설명 |
|------|------|------|
| SQLite DB | `./data/` | 일정, 대화 기록 |
| 환경 변수 | `.env` | API 키 등 민감 정보 |

### 백업 명령어

```bash
# 데이터 백업
cp -r ./data ./backup/data_$(date +%Y%m%d)

# .env 백업 (보안 주의!)
cp .env ./backup/.env_$(date +%Y%m%d)
```

### 복구 명령어

```bash
# 데이터 복구
docker compose down
cp -r ./backup/data_20241230/* ./data/
docker compose up -d
```

---

## 🚨 긴급 대응 절차

### 서비스 다운 시

1. **Slack 알림 확인** (Uptime Kuma)
2. **로그 확인**
   ```bash
   docker logs --tail 50 panager
   ```
3. **컨테이너 재시작**
   ```bash
   docker compose restart panager
   ```
4. **상태 확인**
   ```bash
   docker compose ps
   ```

### 에러 발생 시

1. **Slack 알림 확인** (LoggiFly)
2. **Dozzle에서 상세 로그 확인**
3. **필요 시 재시작**
   ```bash
   docker compose restart panager
   ```

### API 장애 시

| API | 확인 방법 | 대응 |
|-----|----------|------|
| Groq | https://status.groq.com | 임시 대체 모델 사용 |
| OpenWeatherMap | API 호출 테스트 | API 키 확인 |
| Slack | https://status.slack.com | 기다리기 |

---

## 🧹 정기 유지보수

### 주간 작업

- [ ] Dozzle에서 에러 로그 확인
- [ ] Beszel에서 리소스 사용량 확인
- [ ] 디스크 용량 확인

### 월간 작업

- [ ] Docker 이미지 정리
  ```bash
  docker system prune -a
  ```
- [ ] 데이터 백업
- [ ] 보안 업데이트 확인

---

## 📞 연락처

- **GitHub Issues**: https://github.com/j5hjun/panager/issues
- **Slack 채널**: #panager-alerts

---

## 🔗 관련 문서

- [배포 가이드](./DEPLOYMENT.md)
- [README](../README.md)
