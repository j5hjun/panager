"""
Directions Entity 테스트

길찾기 데이터 모델을 검증합니다.
"""

from datetime import datetime


class TestDirectionsData:
    """DirectionsData 엔티티 테스트"""

    def test_directions_data_can_be_imported(self):
        """DirectionsData를 import 할 수 있음"""
        from src.core.entities.directions import DirectionsData

        assert DirectionsData is not None

    def test_directions_data_creation(self):
        """DirectionsData 생성"""
        from src.core.entities.directions import DirectionsData

        data = DirectionsData(
            origin="창동역",
            destination="강남역",
            duration_minutes=45,
            distance_meters=15000,
            fare=1500,
            transfer_count=1,
            departure_time=datetime(2025, 1, 15, 9, 0),
            arrival_time=datetime(2025, 1, 15, 9, 45),
            steps=[
                {"mode": "SUBWAY", "line": "4호선", "from": "창동역", "to": "동대문역사문화공원역"},
                {"mode": "SUBWAY", "line": "2호선", "from": "동대문역사문화공원역", "to": "강남역"},
            ],
        )

        assert data.origin == "창동역"
        assert data.destination == "강남역"
        assert data.duration_minutes == 45
        assert data.transfer_count == 1
        assert len(data.steps) == 2

    def test_directions_data_to_message(self):
        """to_message() 포맷팅"""
        from src.core.entities.directions import DirectionsData

        data = DirectionsData(
            origin="창동역",
            destination="강남역",
            duration_minutes=45,
            distance_meters=15000,
            fare=1500,
            transfer_count=1,
            departure_time=datetime(2025, 1, 15, 9, 0),
            arrival_time=datetime(2025, 1, 15, 9, 45),
            steps=[
                {"mode": "SUBWAY", "line": "4호선", "from": "창동역", "to": "동대문역사문화공원역"},
                {"mode": "SUBWAY", "line": "2호선", "from": "동대문역사문화공원역", "to": "강남역"},
            ],
        )

        message = data.to_message()

        assert "창동역" in message
        assert "강남역" in message
        assert "45분" in message or "45" in message
        assert "환승" in message or "1회" in message

    def test_directions_data_to_brief(self):
        """to_brief() 간략 정보"""
        from src.core.entities.directions import DirectionsData

        data = DirectionsData(
            origin="창동역",
            destination="강남역",
            duration_minutes=45,
            distance_meters=15000,
            fare=1500,
            transfer_count=1,
            departure_time=None,
            arrival_time=None,
            steps=[],
        )

        brief = data.to_brief()

        assert "창동역" in brief
        assert "강남역" in brief
        assert "45" in brief


class TestRouteStep:
    """RouteStep 클래스 테스트"""

    def test_route_step_creation(self):
        """RouteStep 생성"""
        from src.core.entities.directions import RouteStep

        step = RouteStep(
            mode="SUBWAY",
            line="4호선",
            start_name="창동역",
            end_name="동대문역사문화공원역",
            duration_minutes=20,
            distance_meters=8000,
        )

        assert step.mode == "SUBWAY"
        assert step.line == "4호선"
        assert step.start_name == "창동역"
        assert step.duration_minutes == 20

    def test_route_step_to_string(self):
        """RouteStep 문자열 변환"""
        from src.core.entities.directions import RouteStep

        step = RouteStep(
            mode="SUBWAY",
            line="4호선",
            start_name="창동역",
            end_name="동대문역사문화공원역",
            duration_minutes=20,
            distance_meters=8000,
        )

        step_str = str(step)

        assert "4호선" in step_str
        assert "창동역" in step_str
