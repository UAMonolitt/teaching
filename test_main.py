from fastapi.testclient import TestClient
from main import app
import pytest, sqlite3, random
from pytest import param

client = TestClient(app=app)

def test_new_db():
    token = {}
    with sqlite3.connect('database.db') as cursor:
        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('DROP TABLE IF EXISTS screenshots')
        cursor.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT, total_screenshots INT, join_date TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS screenshots(screenshot_name TEXT, screenshot_date TEXT, image_url TEXT, website_url TEXT, user_id INTEGER, delete_after REAL)')    

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
    
@pytest.mark.skip
@pytest.mark.parametrize('url, screenshot_name, expiration, response_code', (
    pytest.param('https://google.com', 'google.com', None, 200, id='google.com, no expire'), 
    pytest.param('https://google.com', 'google.com', 61, 200, id='google.com, expire'),
    pytest.param('https://google.com', None, 61, 200, id='google.com, no name'),
    pytest.param('https://google.com', None, None, 200, id='google.com, no expire, no name'),  
    param({'screenshot_name':'google.com', 'delete_after': None}, id='No expire'),
    param({'screenshot_name': None, 'delete_after': 55}, id='No name'),  
    param({'screenshot_name': None, 'delete_after': None}, id='No name, No expire'),
        pytest.param('google.com', None, None, 200, id='google.com without https'), 
        pytest.param('https://nkladj.com', None, None, 404, id='not existing website'), 
        pytest.param('ahdia', None, None, 404, id='random characters'),
        pytest.param('', None, None, 404, id='empty string')))
def test_basic(url: str, screenshot_name: str, expiration: float, response_code: int):
    response = client.post('/save_screenshot', json={'screenshot_name': screenshot_name, 'delete_after': expiration, 'url': url}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == response_code
    #Исправить это

@pytest.mark.errorr
@pytest.mark.parametrize('payload', (
    param({'screenshot_name': '', 'delete_after': 61}, id='too short name'),
    param({'screenshot_name': str(random.randbytes(51)), 'delete_after': 61}, id='too long name'),
    param({'screenshot_name': 'google.com','delete_after': 55}, id='small expire'), 
    param({'screenshot_name': 'google.com', 'delete_after': 999999999999}, id='big expire'), 
    param({'screenshot_name': '', 'delete_after': 61}, id='bad name'),
    param({'screenshot_name':'google.com', 'delete_after': 'hi'}, id='bad expire')
))
def test_422_error_on_save_screenshot(payload: dict):
    global token
    payload['url'] = 'https://google.com'
    response = client.post('/save_screenshot', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 422


@pytest.mark.token
def test_token():
    global token
    response = client.post('/test_token', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert 'sub' in response.json().keys() and response.json()['sub'] == '1'
    assert 'exp' in response.json().keys()