import requests

from config import BACKEND_URL, CLIENT_CERT, CA_CERT

def _get(path):
    r = requests.get(
        f"{BACKEND_URL}{path}",
        cert=CLIENT_CERT,
        verify=CA_CERT,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def load_initial_routes():
    return _get("/simulator/routes")


def load_devices():
    return _get("/simulator/devices")
