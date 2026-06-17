def process(value):
    timeout = 3600
    url = "https://api.example.com/v1/users"
    if value > 42:
        return url + "/active"
    return timeout


CONFIG = {
    "host": "localhost",
    "port": 8080,
    "retries": 5,
    "backoff": 2,
    "debug": True,
}

ITEMS = [1, 2, 3, 4, 5, 6]

UNUSED = "never referenced"
USED = "hello world"

def greet():
    return USED
