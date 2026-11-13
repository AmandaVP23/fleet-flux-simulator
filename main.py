import asyncio

from backend_client import load_devices, load_initial_routes
from simulator import Simulator


def main():
    print("Hello from fleet-flux-simulator!")

    devices = load_devices();
    routes = load_initial_routes();

    print(devices)

    simulator = Simulator(routes, devices)
    asyncio.run(simulator.run())    


if __name__ == "__main__":
    main()


