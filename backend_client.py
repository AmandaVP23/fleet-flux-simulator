import requests

from config import BACKEND_URL, CLIENT_CERT, CA_CERT

_session = requests.Session()
_session.cert = CLIENT_CERT
_session.verify = CA_CERT


def _get(path):
    r = _session.get(f"{BACKEND_URL}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def load_initial_routes():
    return _get("/simulator/routes")


def load_devices():
    return _get("/simulator/devices")


def get_route_details(routeId):
    r = _session.get(f"/simulator/routes/{routeId}/details")

    if r.status_code == 200:
        return r.json()

    return None