import pytest, random
from pytest import param

standart_payload = {'screenshot_name':'new_screenshot', 'url': 'https://google.com'}

@pytest.fixture(scope='session')
async def register_fixture(client):
    info = {'username': 'UAMonolit', 'password': 'Sigma228'}
    await client.post('/register', json=info)
    return info

@pytest.fixture(scope='session')
async def token(client, register_fixture):
    response = await client.post('/login', json=register_fixture)
    return response.json()['token']

@pytest.mark.asyncio
@pytest.mark.parametrize('username, password, status_code', (
        pytest.param('UAMonolit', 'Sigma228', 200, id='New user'),
        pytest.param('UAMonolit', 'Sigma228', 400, id='User exists error')))
async def test_register(username, password, status_code, client):
    response = await client.post('/register', json={'username': username, 'password': password})
    assert response.status_code == status_code


@pytest.mark.parametrize('username, password, status_code', (
        pytest.param('UAMonolit', 'Sigma228', 200, id='Working inputs'),
        pytest.param('Some', 'wrong_pass', 400, id='Wrong inputs'),
        pytest.param('', 'some_password', 422, id='Empty username'),
        pytest.param('some_username', '', 422, id='Empty password')
))
async def test_login(username, password, status_code, client):
    responce = await client.post('/login', json={'username': username, 'password': password})
    if username == 'UAMonolit':
        token = responce.json()
        token = token['token']
    assert responce.status_code == status_code
   
@pytest.mark.parametrize('payload', (
    param(standart_payload, id='standart google.com'),
    param(standart_payload | {'delete_after': 61}, id='google.com, no name'),
    param(standart_payload | {'url': 'google.com'}, id='google.com without https'),
    param(standart_payload | {'url': 'https://youtube.com'}, id='another website (youtube.com)'),
    param(standart_payload | {'url': 'youtube.com'}, id='another website (youtube.com) without https')
    ))
async def test_no_error_on_save_screenshot(token, payload: dict, client):
    response = await client.post('/screenshots/new', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200

@pytest.mark.parametrize('payload', (
    param(standart_payload | {'screenshot_name': 'a'}, id='too short name'),
    param(standart_payload | {'screenshot_name': str(random.randbytes(51))}, id='too long name'),
    param(standart_payload | {'screenshot_name': '     '}, id='only whitespaces name'),
    param(standart_payload | {'url': ''}, id='empty string on url'),
    param(standart_payload | {'url': '           '}, id='only whitespaces url'),
))
async def test_422_error_on_save_screenshot(token, payload: dict, client):
    response = await client.post('/screenshots/new', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 422

@pytest.mark.parametrize('payload', (
        param(standart_payload | {'url': 'https://pop0-1mcndjaasdl.com'}, id='Non-existing website'),
        param(standart_payload | {'url': 'pop0-1mcndjaasdl.com'}, id='Non-existing website without https'),
))
async def test_404_error_on_save_screenshot(token, payload: dict, client):
    response = await client.post('/screenshots/new', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 404
#
#@pytest.mark.token
#def test_token():
#    global token
#    response = client.post('/test_token', headers={'Authorization': f'Bearer {token}'})
#    assert response.status_code == 200
#    assert 'sub' in response.json().keys() and response.json()['sub'] == '1'
#    assert 'exp' in response.json().keys()