import json
from typing import List

import dict_deep
import settings
import bigcorp
import uvicorn
from fastapi import FastAPI, Query, HTTPException




def init_db():
    """
    Init and load in-memory key value store for departments, offices and managers.
    :return: dictionary with departments and offices that can be accessible by their keys
    """
    departments_list = json.loads(open('data/departments.json').read())
    offices_list = json.loads(open('data/offices.json').read())

    # use the same "foreign" keys which would be looked up on the expansion
    # TODO: make a mapping dict to preserve naming conventions not specified yet
    data = {
        'department': {},
        'superdepartment': {},
        'office': {},
        'manager': {}
    }
    for department in departments_list:
        data['department'][department['id']] = department
    data['superdepartment'] = data['department']

    for office in offices_list:
        data['office'][office['id']] = office

    return data


app = FastAPI()
db = init_db()


def expand_employee(target, paths):
    """
    get the values given a path from the target, likely to be an integer key.
    lookup the "foreign" keys from in-memory db
    set the values given a path to the target.
    :param target: employee
    :param paths: dot noted keys
    :return: enritched employee
    """
    # resolve the path for each recursive key path
    obj = target.copy()
    for key_path in paths:
        _id = dict_deep.deep_get(obj, key_path)
        if type(_id) is dict:
            _id = _id['id']

        # skip also null "foreign keys"
        if not _id:
            continue

        # root key comes first
        db_key = key_path.split(".")[-1]

        try:
            record = db[db_key][_id].copy()
        except KeyError:
            raise KeyError(f"Could not resolve path for '{key_path}'")
        except Exception:
            raise

        dict_deep.deep_set(obj, key_path, record)
    return obj


def resolve_manager_dependencies(employees, levels):
    """
    deep expansions for managers could be received, the source for this expansion is remote,
    use in-memory store to avoid making unnecessary calls to the bigcorp api by accumulating the missing
    manager employees and making a batch search on the API and write all the employee records in memory.
    :param employees: to be expanded
    :param levels: deepness to be expand, for intance manager is 1 level, manager.manager is 2 levels, etc.
    :return: managers that are not longer missing and written on in-memory store.
    """
    missing_managers_ids = []

    # overwrite in-memory store
    for employee in employees:
        db['manager'][employee['id']] = employee

    # look missing records by iterating the different required levels
    for _ in range(levels):
        for employee in db['manager'].values():
            manager_id = employee.get("manager")

            # ignore null keys
            if not manager_id:
                continue

            if manager_id not in db['manager']:
                missing_managers_ids.append(manager_id)

        # batch lookup the missing employees and write them in memory
        missing_employees = bigcorp.proxy_request_employees_by_id(missing_managers_ids)
        for missing_employee in missing_employees:
            db['manager'][missing_employee['id']] = missing_employee

    return missing_managers_ids


def get_paths(expand):
    """
    analyze the "expand" api param so the dependencies could be looked up and satisfied using the expander strategy.
    :param expand: example: office, manager, manager.office, manager.manager.manager.manager, etc.
    :return:
    """
    paths = []
    manager_paths = []
    for dotted_keys in expand:
        key = str
        dotted_keys = dotted_keys.split(".")
        for i, k in enumerate(dotted_keys, 0):
            key = k if i == 0 else f"{key}.{k}"
            if key in paths:
                continue

            paths.append(key)

            # since managers keys requires a different approach,
            # identify all of the paths which only need to expand managers
            if all(name == "manager" for name in dotted_keys):
                manager_paths.append(key)
    return paths, manager_paths


@app.get("/employees")
def list_employees(
        limit: int = Query(
            settings.DEFAULT_LIMIT,
            description="The max number of records returned",
            ge=1, le=1000
        ),
        offset: int = Query(
            settings.DEFAULT_OFFSET,
            description="The index at which to start.",
            ge=0
        ),
        expand: List[str] = Query(
            settings.DEFAULT_EXPAND,
            description="There are four relationships that can be expanded: manager, office, department, "
                        "chain expansions as needed",
        )
):
    try:
        employees = bigcorp.proxy_request_employees(limit, offset)
        results = []

        # identify the expansion keys preserving deepness
        # A.B.C path keys should be expanded and set values on this order: A, A.B, A.B.C
        paths, manager_paths = get_paths(expand)

        # satisfy manager dependencies first so the lookup into the in-memory store always returns an employee
        if manager_paths:
            resolve_manager_dependencies(employees, len(manager_paths))

        # resolve expansion given the recursive key paths using 'deep getters/setters' strategy
        # use the in-memory store to run get by entities then get by ids
        for employee in employees:
            e = expand_employee(employee, paths)
            results.append(e)

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/employees/{employee_id}")
def get_employee(
        employee_id: int,
        expand: List[str] = Query(
            settings.DEFAULT_EXPAND,
            description="There are four relationships that can be expanded: manager, office, department, "
                        "chain expansions as needed",
        )
):
    try:
        result = {}
        employees = bigcorp.proxy_request_employees_by_id([employee_id])
        paths, manager_paths = get_paths(expand)
        if manager_paths:
            resolve_manager_dependencies(employees, len(manager_paths))
        for employee in employees:
            e = expand_employee(employee, paths)
            result = e
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
