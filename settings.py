import os

DEFAULT_LIMIT = os.environ.get('DEFAULT_LIMIT', 100)
DEFAULT_OFFSET = os.environ.get('DEFAULT_OFFSET', 0)
DEFAULT_EXPAND = []
EMPLOYEE_API_URL_BASE = os.environ.get(
    'EMPLOYEE_API_URL_BASE',
    "https://rfy56yfcwk.execute-api.us-west-1.amazonaws.com/bigcorp"
)