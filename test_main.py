from fastapi.testclient import TestClient
from main import app
import pytest, sqlite3
from datetime import datetime, UTC, timedelta

client = TestClient(app=app)

def test_new_db():
    token = {}
    with sqlite3.connect('database.db') as cursor:
        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('DROP TABLE IF EXISTS screenshots')
        cursor.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT, total_screenshots INT, join_date TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS screenshots(screenshot_name TEXT, screenshot_date TEXT, image_url TEXT, website_url TEXT, user_id INTEGER)')    

@pytest.mark.parametrize('url, response_code', (
        pytest.param('https://google.com', 200, id='google.com'), 
        pytest.param('google.com', 200, id='google.com without https'), 
        pytest.param('https://nkladj.com', 404, id='not existing website'), 
        pytest.param('ahdia', 404, id='random characters'),
        pytest.param('', 404, id='empty string')))
def test_basic(url, response_code):
    response = client.get(f'/save_screenshot?url={url}')
    assert response.status_code == response_code

@pytest.mark.parametrize('username, password, status_code', (
        pytest.param('UAMonolit', 'Sigma228', 200, id='New user'),
        pytest.param('UAMonolit', 'Sigma228', 400, id='User exists error'),
        pytest.param('', 'Sigma228', 422, id='Empty username'),
        pytest.param('UAMonolit', '', 422, id='Empty passowrd')))
def test_register(username, password, status_code):
    response = client.post('/register', json={'username': username, 'password': password})
    assert response.status_code == status_code


@pytest.mark.parametrize('username, password, status_code', (
        pytest.param('UAMonolit', 'Sigma228', 200, id='Working inputs'),
        pytest.param('Some', 'wrong_pass', 400, id='Wrong inputs'),
        pytest.param('', 'some_password', 422, id='Empty username'),
        pytest.param('some_username', '', 422, id='Empty password')
))
def test_login(username, password, status_code):
    global token
    responce = client.post('/login', json={'username': username, 'password': password})
    if username == 'UAMonolit':
        token = responce.json()
        token = token['token']
    assert responce.status_code == status_code

@pytest.mark.token
def test_token():
    global token
    response = client.post('/test_token', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert 'sub' in response.json().keys() and response.json()['sub'] == '1'
    assert 'exp' in response.json().keys()