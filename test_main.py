from fastapi.testclient import TestClient
from main import app
import pytest, sqlite3, random
from pytest import param

client = TestClient(app=app)

standart_payload = {'screenshot_name':'aas', 'url': 'https://google.com'}

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
        pytest.param('UAMonolit', '', 422, id='Empty password')))
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
    
@pytest.mark.parametrize('payload', (
    param(standart_payload, id='standart google.com'),
    param(standart_payload | {'delete_after': 61}, id='google.com, no name'),
    param(standart_payload | {'screenshot_name': 'google.com'}, id='No expire'),
    param(standart_payload, id='No name, No expire'),
    param(standart_payload | {'url': 'google.com'}, id='google.com without https'),
    param(standart_payload | {'url': 'https://youtube.com'}, id='another website (youtube.com)'),
    param(standart_payload | {'url': 'youtube.com'}, id='another website (youtube.com) without https')
    ))
def test_no_error_on_save_screenshot(payload: dict):
    response = client.post('/save_screenshot', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200

@pytest.mark.parametrize('payload', (
    param(standart_payload | {'screenshot_name': 'a'}, id='too short name'),
    param(standart_payload | {'screenshot_name': str(random.randbytes(51))}, id='too long name'),
    param(standart_payload | {'delete_after': 0}, id='small expire'), 
    param(standart_payload | {'delete_after': 999999999999}, id='big expire'), 
    param(standart_payload | {'screenshot_name': '     '}, id='only whitespaces name'),
    param(standart_payload | {'delete_after': 'hi'}, id='text expire'),
    param(standart_payload | {'url': ''}, id='empty string on url'),
    param(standart_payload | {'url': '           '}, id='only whitespaces url'),
))
def test_422_error_on_save_screenshot(payload: dict):
    global token
    response = client.post('/save_screenshot', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 422


@pytest.mark.parametrize('payload', (
        param(standart_payload | {'url': 'https://pop0-1mcndjaasdl.com'}, id='Non-existing website'),
        param(standart_payload | {'url': 'pop0-1mcndjaasdl.com'}, id='Non-existing website without https'),
))
def test_404_error_on_save_screenshot(payload: dict):
    global token
    response = client.post('/save_screenshot', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 404

@pytest.mark.token
def test_token():
    global token
    response = client.post('/test_token', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert 'sub' in response.json().keys() and response.json()['sub'] == '1'
    assert 'exp' in response.json().keys()