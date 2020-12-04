from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_limit():
    response = client.get("/employees?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    response_with_limit = client.get("/employees?limit=2")
    assert response_with_limit.status_code == 200
    assert len(response_with_limit.json()) == 2
    response_with_limit_error = client.get("/employees?limit=-1")
    assert response_with_limit_error.status_code == 422


def test_offset():
    response = client.get("/employees?limit=10&offset=0")
    assert response.status_code == 200
    response_with_offset = client.get("/employees?limit=100&offset=1")
    assert response_with_offset.status_code == 200
    assert response.json()[1]["id"] == response_with_offset.json()[0]["id"]


def test_expand_department():
    response = client.get("/employees?limit=1&offset=1")
    assert response.status_code == 200
    assert type(response.json()[0]["department"]) is int

    response_with_expand = client.get("/employees?limit=1&offset=1&expand=department")
    assert response_with_expand.status_code == 200
    assert type(response_with_expand.json()[0]["department"]) is dict
    assert response.json()[0]["department"] == response_with_expand.json()[0]["department"]["id"]

    response_with_expand_deeper = client.get("/employees?limit=1&offset=1&expand=department.superdepartment")
    assert response_with_expand_deeper.status_code == 200
    assert type(response_with_expand_deeper.json()[0]["department"]["superdepartment"]) is dict


def test_expand_office():
    response = client.get("/employees?limit=1&offset=1")
    assert response.status_code == 200
    assert type(response.json()[0]["office"]) is int

    response = client.get("/employees?limit=1&offset=1&expand=office")
    assert response.status_code == 200
    assert type(response.json()[0]["office"]) is dict


def test_expand_manager():
    response0 = client.get("/employees?limit=1&offset=100")
    response1 = client.get("/employees?limit=1&offset=100&expand=manager")
    response2 = client.get("/employees?limit=1&offset=100&expand=manager.manager")
    response3 = client.get("/employees?limit=1&offset=100&expand=manager.manager.manager")

    assert response0.status_code == 200
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    id0 = response0.json()[0]["manager"]
    assert type(id0) is int

    assert type(response1.json()[0]["manager"]) is dict
    id1 = response1.json()[0]["manager"]["id"]
    assert type(id1) is int
    assert id0 == id1

    assert type(response2.json()[0]["manager"]) is dict
    id2 = response2.json()[0]["manager"]["id"]
    assert type(id2) is int
    assert id1 == id2

    assert type(response3.json()[0]["manager"]) is dict
    id3 = response3.json()[0]["manager"]["id"]
    assert type(id3) is int
    assert id2 == id3


def test_expand_combined():
    response = client.get("/employees?limit=1&offset=100&expand=manager.office&expand=manager.department&expand=department&expand=office")
    assert response.status_code == 200
    assert type(response.json()[0]["manager"]) is dict
    assert type(response.json()[0]["manager"]["department"]) is dict
    assert type(response.json()[0]["department"]) is dict
    assert type(response.json()[0]["office"]) is dict
