from app.ACEest_Fitness import app

def test_home():
    tester = app.test_client()
    response = tester.get('/')
    assert response.status_code == 200
