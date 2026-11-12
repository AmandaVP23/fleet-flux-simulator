import os
from dotenv import load_dotenv

load_dotenv()
OSRM_SERVER_URL = os.environ["OSRM_SERVER_URL"].rstrip("/")
BACKEND_URL = os.getenv("BACKEND_URL", "https://localhost:8443").rstrip("/")
CLIENT_CERT = ("certs/simulator.crt", "certs/simulator.key")
CA_CERT = "certs/ca.crt"