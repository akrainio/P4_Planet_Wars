import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from math import inf
from timeit import default_timer as time


def start_timer(state, data, parameters):
    data["timer"] = time()
    return True

    
def initialize_ships_and_deployments(state, data, parameters):
    data["num_available_ships"] = 0
    data["available_ships"] = {}
    for planet in state.my_planets():
        data["num_available_ships"] += planet.num_ships - 1
        data["available_ships"][planet] = planet.num_ships - 1
    data["deployments"] = []
    return True


def find_focus_point(state, data, parameters):
    return True


def deploy_fleet(state, data, parameters):
    """
        Attempts to make a deployment defined in the deployments priority queue
        
        Returns True if deployment was successfully made and ships remain
    """
    ships = data["available_ships"]
    deployments = data["deployments"]
    
    if not deployments:
        return False
        
    score, target, num_ships = deployments.get()
    
    while num_ships > 0 and ships:
        closest_planet = None
        closest_planet_distance = inf
        for planet in ships.keys():
            planet_distance = state.distance(planet, target)
            if planet_distance < closest_planet_distance:
                closest_planet = planet
                closest_planet_distance = planet_distance
        
        fleet_size = min(planet.num_ships, num_ships)
        issue_order(state, closest_planet, target, fleet_size)
        
        num_ships -= fleet_size
        ships[closest_planet] -= fleet_size
        if ships[closest_planet] <= 0:
            del ships[closest_planet]
        
    return ships