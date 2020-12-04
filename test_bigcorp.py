import bigcorp


def test_bigcorp():
    res = bigcorp.proxy_request_employees_by_id([1])
    assert res[0]["id"] == 1

