from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]


def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]


def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'non.existent@mail.com'})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'New User',
        'email': 'new.user@mail.com',
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    data = response.json()

    print(data)  # Отладочный вывод

    # Проверка, что ответ содержит ID (вместо словаря)
    assert isinstance(data, int)  # Проверяем, что это число (ID)

    # Если сервер возвращает ID, нужно проверить его
    assert data > 0  # Проверка, что ID больше 0


def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_email = users[0]['email']
    new_user = {
        'name': 'Conflict User',
        'email': existing_email,
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 409  # Ожидаем код 409 Conflict
    assert response.json() == {"detail": "User with this email already exists"}


def test_delete_user():
    '''Удаление пользователя'''
    # Сначала создаём пользователя
    new_user = {
        'name': 'To Delete',
        'email': 'delete.me@mail.com',
    }
    create_response = client.post("/api/v1/user", json=new_user)

    # Проверка, что ответ содержит ID
    create_data = create_response.json()
    print(f"Созданный пользователь: {create_data}")  # Отладочный вывод
    assert isinstance(create_data, int)  # Проверяем, что это число (ID)
    user_id = create_data

    # Проверяем, что пользователь действительно был создан
    assert user_id > 0  # Проверяем, что ID валидный

    # Удаляем пользователя
    delete_response = client.delete(f"/api/v1/user/{user_id}")
    print(f"Ответ на удаление: {delete_response.status_code}")  # Отладочный вывод
    assert delete_response.status_code == 204  # Ожидаем код 204 (успешное удаление)

    # Проверяем, что пользователь удалён
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    print(f"Ответ на проверку удаления: {get_response.status_code}")  # Отладочный вывод
    assert get_response.status_code == 404  # Ожидаем, что пользователь не найден
