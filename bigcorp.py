import settings
import requests


def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    :param lst: target
    :param n: number of items
    :return: list of chunks
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def proxy_request_employees(limit=settings.DEFAULT_LIMIT, offset=settings.DEFAULT_OFFSET):
    """
    Call lambda function for the bigcorp employees records.
    :param limit: max records to be retrieved
    :param offset: pagination
    :return: just a serialized list of employee records
    """

    params = {
        'limit': limit,
        'offset': offset
    }
    res = requests.get(f"{settings.EMPLOYEE_API_URL_BASE}/employees", params)
    return res.json()


def proxy_request_employees_by_id(identifiers):
    """
    Call lambda function for the bigcorp employees records.
    Seems like this api returns max 100 items, so better chunk identifiers
    :param identifiers: list of ids of the employee to be looked up
    :return: just a serialized employee record
    """
    employees = []

    for ids in chunks(identifiers, 100):
        params = {
            'id': ids
        }
        res = requests.get(f"{settings.EMPLOYEE_API_URL_BASE}/employees", params)
        employees = employees + res.json()
    return employees
