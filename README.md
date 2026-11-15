# Fleet Flux Simulator

Simulates a fleet of vehicles driving along OSRM routes and reporting to the backend.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python >= 3.14 is managed by uv)
- A running OSRM server (provisioned outside this project)
- The backend running, with client certificates in `certs/` (`simulator.crt`, `simulator.key`, `ca.crt`)

## Configuration

Create a `.env` file in the project root:

```env
OSRM_SERVER_URL=http://localhost:5000
BACKEND_URL=https://localhost:8443   # optional, default shown
TICK_SECONDS=5                       # optional, default shown
```

## Run

Install dependencies:

```bash
uv sync
```

Start the simulator:

```bash
uv run main.py
```
