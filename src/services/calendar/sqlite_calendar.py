"""
SQLite 기반 일정 서비스

로컬 SQLite DB를 사용하여 일정을 관리합니다.
"""

import logging
import sqlite3
from datetime import datetime, timedelta

from src.core.entities.calendar import Schedule

logger = logging.getLogger(__name__)


class CalendarService:
    """
    일정 서비스

    SQLite를 사용하여 일정을 저장하고 조회합니다.
    """

    def __init__(self, db_path: str = "data/calendar.db"):
        """
        CalendarService 초기화

        Args:
            db_path: SQLite DB 경로 (":memory:"면 메모리 DB)
        """
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._init_db()

        logger.info(f"CalendarService 초기화 완료 (db={db_path})")

    def _init_db(self) -> None:
        """데이터베이스 초기화 및 테이블 생성"""
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

        cursor = self._conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schedules (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                location TEXT,
                description TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def add_schedule(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime | None = None,
        location: str = "",
        description: str = "",
    ) -> str:
        """
        일정 추가

        Args:
            title: 일정 제목
            start_time: 시작 시간
            end_time: 종료 시간 (선택)
            location: 장소 (선택)
            description: 설명 (선택)

        Returns:
            생성된 일정 ID
        """
        schedule_id = f"{int(start_time.timestamp())}_{hash(title) % 10000}"
        created_at = datetime.now().isoformat()

        if not self._conn:
            raise RuntimeError("Database connection not initialized")

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO schedules (id, title, start_time, end_time, location, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                schedule_id,
                title,
                start_time.isoformat(),
                end_time.isoformat() if end_time else None,
                location,
                description,
                created_at,
            ),
        )
        self._conn.commit()

        logger.info(f"일정 추가: {title} ({start_time})")
        return schedule_id

    def get_schedule(self, schedule_id: str) -> Schedule | None:
        """
        일정 조회

        Args:
            schedule_id: 일정 ID

        Returns:
            Schedule 객체 또는 None
        """
        if not self._conn:
            raise RuntimeError("Database connection not initialized")

        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_schedule(row)

    def get_schedules_by_date(self, date: datetime) -> list[Schedule]:
        """
        특정 날짜의 일정 조회

        Args:
            date: 조회할 날짜

        Returns:
            일정 목록
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        if not self._conn:
            raise RuntimeError("Database connection not initialized")

        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT * FROM schedules
            WHERE start_time >= ? AND start_time <= ?
            ORDER BY start_time
            """,
            (start_of_day.isoformat(), end_of_day.isoformat()),
        )

        return [self._row_to_schedule(row) for row in cursor.fetchall()]

    def get_today_schedules(self) -> list[Schedule]:
        """오늘의 일정 조회"""
        return self.get_schedules_by_date(datetime.now())

    def get_tomorrow_schedules(self) -> list[Schedule]:
        """내일의 일정 조회"""
        tomorrow = datetime.now() + timedelta(days=1)
        return self.get_schedules_by_date(tomorrow)

    def delete_schedule(self, schedule_id: str) -> bool:
        """
        일정 삭제

        Args:
            schedule_id: 삭제할 일정 ID

        Returns:
            삭제 성공 여부
        """
        if not self._conn:
            raise RuntimeError("Database connection not initialized")

        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
        self._conn.commit()

        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"일정 삭제: {schedule_id}")
        return deleted

    def format_schedule_list(self, schedules: list[Schedule]) -> str:
        """
        일정 목록을 포맷된 문자열로 변환

        Args:
            schedules: 일정 목록

        Returns:
            포맷된 문자열
        """
        if not schedules:
            return "일정이 없습니다."

        lines = []
        for schedule in schedules:
            lines.append(schedule.to_brief())

        return "\n".join(lines)

    def _row_to_schedule(self, row: sqlite3.Row) -> Schedule:
        """SQLite Row를 Schedule 객체로 변환"""
        return Schedule(
            id=row["id"],
            title=row["title"],
            start_time=datetime.fromisoformat(row["start_time"]),
            end_time=(datetime.fromisoformat(row["end_time"]) if row["end_time"] else None),
            location=row["location"] or "",
            description=row["description"] or "",
        )

    def __del__(self):
        """데이터베이스 연결 종료"""
        if self._conn:
            self._conn.close()
