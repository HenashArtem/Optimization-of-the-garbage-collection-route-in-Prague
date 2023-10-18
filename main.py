import requests
import random
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import numpy as np

API_GOLEMIO_URL = "https://api.golemio.cz/v2/sortedwastestations"
API_ACCESS_TOKEN = ""  # Enter your API_ACCESS_TOKEN here


class Particle:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity
        self.best_position = position
        self.best_fitness = float('inf')


class RouteOptimizer:
    def __init__(self, stations):
        self.stations = stations

    def distance_calculation(self, lat1, lon1, lat2, lon2):
        coord1 = (lat1, lon1)
        coord2 = (lat2, lon2)
        distance = geodesic(coord1, coord2).kilometers
        return distance

    def route_cost_calculation(self, route):
        total_cost = 0.0
        for i in range(len(route) - 1):
            start_station = self.stations[int(route[i])]
            end_station = self.stations[int(route[i + 1])]
            distance = self.distance_calculation(
                start_station.get("geometry").get("coordinates")[0],
                start_station.get("geometry").get("coordinates")[1],
                end_station.get("geometry").get("coordinates")[0],
                end_station.get("geometry").get("coordinates")[1]
            )
            total_cost += distance
        return total_cost

    def route_optimization(self):
        num_stations = len(self.stations)
        num_particles = 100
        max_iterations = 100

        particles = []
        for _ in range(num_particles):
            position = list(range(num_stations))
            velocity = np.zeros(num_stations)
            particle = Particle(position, velocity)
            particles.append(particle)

        global_best_position = particles[0].position
        global_best_fitness = float('inf')

        for _ in range(max_iterations):
            for particle in particles:
                w = 0.5
                c1 = 1.5
                c2 = 1.5

                new_velocity = (
                        w * particle.velocity +
                        c1 * random.random() * (np.array(particle.best_position) - np.array(particle.position)) +
                        c2 * random.random() * (np.array(global_best_position) - np.array(particle.position))
                )
                particle.velocity = new_velocity

                new_position = particle.position + particle.velocity
                particle.position = new_position

                particle_fitness = self.route_cost_calculation(particle.position)
                if particle_fitness < particle.best_fitness:
                    particle.best_position = particle.position
                    particle.best_fitness = particle_fitness

                if particle_fitness < global_best_fitness:
                    global_best_position = particle.position
                    global_best_fitness = particle_fitness

        best_route = global_best_position
        return best_route

    def route_visualization(self, route):
        lats = []
        lngs = []
        for station_idx in route:
            station = self.stations[station_idx]
            lats.append(station.get("geometry").get("coordinates")[0])
            lngs.append(station.get("geometry").get("coordinates")[1])

        plt.figure(figsize=(10, 6))
        plt.plot(lngs, lats, marker="*", linestyle=":", color="red")
        plt.plot(lngs[0], lats[0], marker="X", color="orange", label="Start")
        plt.plot(lngs[-1], lats[-1], marker="X", color="purple", label="End")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Optimized Waste Collection Route")
        plt.legend()
        plt.grid(True)
        plt.show()


def get_all_waste_collection_stations():
    headers = {'X-Access-Token': f'{API_ACCESS_TOKEN}'}
    params = {'limit': '10'}
    response = requests.get(API_GOLEMIO_URL, headers=headers, params=params)
    data = response.json()
    return data["features"]


def main():
    stations = get_all_waste_collection_stations()
    optimizer = RouteOptimizer(stations)
    route = optimizer.route_optimization()
    route = [int(station_idx) for station_idx in route]
    total_distance = optimizer.route_cost_calculation(route)

    print("Optimized Route:")
    optimized_stations = [stations[station_idx] for station_idx in route]
    for station in optimized_stations:
        station_id = station.get('properties').get('id')
        address = station.get('properties').get('name')
        print(f"- Waste station id: {station_id}, Address: {address}")

    print(f"\nSummary Distance: {total_distance:.2f} km")

    optimizer.route_visualization(route)


if __name__ == "__main__":
    main()
