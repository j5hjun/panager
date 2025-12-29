#!/bin/bash
# 패니저 배포 스크립트
# HP T620 서버에서 실행

set -e

echo "🚀 패니저 배포 시작..."

# 변수 설정
REPO_DIR="${HOME}/panager"
IMAGE="ghcr.io/j5hjun/panager:latest"

# 저장소 디렉토리로 이동
cd "$REPO_DIR" || {
    echo "❌ 디렉토리가 없습니다: $REPO_DIR"
    exit 1
}

# 최신 코드 가져오기
echo "📥 최신 코드 가져오는 중..."
git pull origin main

# 최신 이미지 가져오기
echo "🐳 Docker 이미지 가져오는 중..."
docker pull "$IMAGE" || {
    echo "⚠️ 이미지 pull 실패, 로컬 빌드 시도..."
    docker compose build
}

# 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 중지..."
docker compose down || true

# 새 컨테이너 시작
echo "▶️ 새 컨테이너 시작..."
docker compose up -d

# 상태 확인
echo "✅ 배포 완료!"
docker compose ps

# 로그 확인 (5초)
echo ""
echo "📜 최근 로그 (5초):"
timeout 5 docker compose logs -f || true

echo ""
echo "🎉 배포 성공! 로그 확인: docker compose logs -f"
