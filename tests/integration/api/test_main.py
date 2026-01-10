from fastapi.testclient import TestClient

# We will need to import 'app' later, but for now this import will fail, 
# satisfying the "Red" condition of TDD.
try:
    from app.main import app
    client = TestClient(app)
except ImportError:
    client = None

def test_health_check():
    """
    Test the health check endpoint.
    This test is expected to fail initially because:
    1. app.main module doesn't exist yet (ImportError)
    2. or if it did, the endpoint might not be implemented
    """
    assert client is not None, "Application not initialized"
    
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Proactive Manager API is running"}
