# OSRM Setup – Portugal & Spain (macOS)

This guide explains how to download OpenStreetMap data for Portugal and Spain, merge the extracts, generate an OSRM routing dataset, and run OSRM natively on macOS without Docker.

## 1. Prerequisites

Install Homebrew if it is not already installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install the required tools:

```bash
brew update
brew install osrm-backend osmium-tool wget
```

Check installations:

```bash
osrm-extract --version
osrm-partition --version
osrm-customize --version
osmium --version
```

## 2. Create the project directories

From your project root:

```bash
mkdir -p data/osm
mkdir -p data/osrm
mkdir -p logs
```

Directory structure:

```text
project/
├── data/
│   ├── osm/
│   │   ├── portugal-latest.osm.pbf
│   │   ├── spain-latest.osm.pbf
│   │   └── portugal-spain.osm.pbf
│   │
│   └── osrm/
│       ├── portugal-spain.osrm
│       └── portugal-spain.osrm.*
│
├── logs/
├── python/
└── OSRM_SETUP.md
```

## 3. Download OpenStreetMap extracts

The following commands use Geofabrik's official regional download service.

```bash
cd data/osm
```

Download Portugal:

```bash
wget https://download.geofabrik.de/europe/portugal-latest.osm.pbf
```

Download Spain:

```bash
wget https://download.geofabrik.de/europe/spain-latest.osm.pbf
```

Check downloaded files:

```bash
ls -lh *.osm.pbf
```

## 4. Merge Portugal and Spain

Use Osmium to merge both PBF files:

```bash
osmium merge \
  portugal-latest.osm.pbf \
  spain-latest.osm.pbf \
  -o portugal-spain.osm.pbf
```

Check the merged file:

```bash
ls -lh portugal-spain.osm.pbf
```

Optional: validate the merged PBF:

```bash
osmium fileinfo portugal-spain.osm.pbf
```

## 5. Generate the OSRM routing dataset

Return to the project root:

```bash
cd ../..
```

Set the dataset paths:

```bash
INPUT="data/osm/portugal-spain.osm.pbf"
OUTPUT="data/osrm/portugal-spain"
```

### Step 1 – Extract road network

For car routing, use the standard OSRM car profile:

```bash
osrm-extract \
  -p "$(brew --prefix osrm-backend)/share/osrm/profiles/car.lua" \
  "$INPUT" \
  -o "$OUTPUT"
```

This generates the initial OSRM dataset.

### Step 2 – Partition the routing graph

```bash
osrm-partition "$OUTPUT.osrm"
```

### Step 3 – Customize the routing graph

```bash
osrm-customize "$OUTPUT.osrm"
```

The preprocessing pipeline uses the MLD (Multi-Level Dijkstra) algorithm.

**Important:** Run partition and customize after extraction. If you change the input PBF or routing profile, regenerate the dataset.

## 6. Start the OSRM server

Run the routing server:

```bash
osrm-routed \
  --algorithm mld \
  data/osrm/portugal-spain.osrm \
  --port 5000
```

The server should now be available at:

```text
http://localhost:5000
```

Keep this terminal open while using the routing service.

## 7. Test the routing API

Open another terminal and execute:

```bash
curl "http://localhost:5000/route/v1/driving/-9.1393,38.7223;-8.6291,41.1579?overview=false"
```

This example calculates a driving route between Lisbon and Porto.

A successful response should contain:

- `code: Ok`
- `routes`
- `distance` (meters)
- `duration` (seconds)

## 8. Use OSRM from Python

Install the Python HTTP client:

```bash
pip install requests
```

Example Python script:

```python
import requests

OSRM_URL = "http://localhost:5000"

def get_route(start_lon, start_lat, end_lon, end_lat):
    url = (
        f"{OSRM_URL}/route/v1/driving/"
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
    )

    params = {
        "overview": "false",
        "steps": "true"
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    result = response.json()

    if result["code"] != "Ok":
        raise RuntimeError(result)

    route = result["routes"][0]

    return {
        "distance_km": route["distance"] / 1000,
        "duration_minutes": route["duration"] / 60
    }


if __name__ == "__main__":
    route = get_route(
        -9.1393, 38.7223,  # Lisbon
        -8.6291, 41.1579   # Porto
    )

    print(route)
```

## 9. Updating the OpenStreetMap data

When you want to refresh the routing dataset:

```bash
cd data/osm

wget -O portugal-latest.osm.pbf \
  https://download.geofabrik.de/europe/portugal-latest.osm.pbf

wget -O spain-latest.osm.pbf \
  https://download.geofabrik.de/europe/spain-latest.osm.pbf

osmium merge \
  portugal-latest.osm.pbf \
  spain-latest.osm.pbf \
  -o portugal-spain.osm.pbf

cd ../..
```

Then regenerate the OSRM dataset:

```bash
INPUT="data/osm/portugal-spain.osm.pbf"
OUTPUT="data/osrm/portugal-spain"

osrm-extract \
  -p "$(brew --prefix osrm-backend)/share/osrm/profiles/car.lua" \
  "$INPUT" \
  -o "$OUTPUT"

osrm-partition "$OUTPUT.osrm"
osrm-customize "$OUTPUT.osrm"
```

Restart the OSRM server after regeneration.

## 10. Git configuration

The OSRM datasets can occupy several gigabytes and should not be committed to Git.

Add the following to `.gitignore`:

```gitignore
# OpenStreetMap source data
*.osm.pbf

# OSRM generated datasets
*.osrm
*.osrm.*

# OSRM logs
logs/
```

The downloaded and generated files remain available locally.

## 11. Useful commands

Check dataset size:

```bash
du -sh data/osm data/osrm
```

List generated OSRM files:

```bash
ls -lh data/osrm/
```

Check whether the server is running:

```bash
curl http://localhost:5000/nearest/v1/driving/-9.1393,38.7223
```

Find the process using port 5000:

```bash
lsof -i :5000
```

Stop the server:

```bash
kill $(lsof -ti :5000)
```

## 12. Important notes

- OSRM uses longitude, latitude coordinate order.
- The example uses the car routing profile.
- MLD is suitable for general-purpose routing and supports customization.
- The OSRM server must be running before Python can send routing requests.
- The generated routing files are platform-specific build artifacts and should be regenerated when changing the source data, profile, or OSRM version.
- Ensure you have sufficient free disk space for the original extracts, merged PBF and generated OSRM dataset.
- For production, consider running OSRM as a background service and monitoring its memory consumption.

## Problems
To avoid having versions problems:
```uv run python -m osrm osrm-extract -p "$(brew --prefix osrm-backend)/share/osrm/profiles/car.lua" osrm-data/portugal-spain.osm.pbf```

## References

- OSRM Backend: https://github.com/Project-OSRM/osrm-backend
- OSRM API documentation: https://project-osrm.org/docs/v5.24.0/api/
- Geofabrik downloads: https://download.geofabrik.de/europe.html
- Osmium Tool: https://osmcode.org/osmium-tool/

---

**Result:** A locally hosted OSRM routing engine covering Portugal and Spain, accessible to your Python applications through `http://localhost:5000` without Docker.
