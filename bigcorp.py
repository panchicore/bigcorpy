import settings
import requests


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
    :param identifiers: list of ids of the employee to be looked up
    :return: just a serialized employee record
    """
    params = {
        'id': identifiers
    }
    res = requests.get(f"{settings.EMPLOYEE_API_URL_BASE}/employees", params)
    return res.json()
