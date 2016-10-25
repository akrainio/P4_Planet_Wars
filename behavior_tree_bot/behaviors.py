import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from math import inf
from timeit import default_timer as time
from queue import PriorityQueue


def start_timer(state, data, parameters):
    """
        Starts the turn timer
    """
    data["timer"] = time()
    return True

    
def initialize_ships_and_deployments(state, data, parameters):
    """
        Creates the available ship map and the deployment priority queue
    """
    data["available_ships"] = {}
    data["deployments"] = PriorityQueue()
    
    # find available ships
    for planet in state.my_planets():
        data["available_ships"][planet] = planet.num_ships - 1
    return True


def find_focus_point(state, data, parameters):
    """
        Finds the central point of our currently held planets
        Used to estimate distances when gauging targets
        Calculation could be adjusted to prioritize planets differently
    """
    data["focus_x"] = 0
    data["focus_y"] = 0  
    for planet in state.my_planets():
        data["focus_x"] += planet.x
        data["focus_y"] += planet.y
    data["focus_x"] /= len(state.my_planets())
    data["focus_y"] /= len(state.my_planets())
    return True


def defense_strategy(state, data, parameters):
    """
        Adds defensive deployments to the deployment priority queue.
    """
    for enemy_fleet in state.enemy_fleets():
        if enemy_fleet.destination_planet.owner == 1:
            pass


def deploy_fleet(state, data, parameters):
    """
        Attempts to make a deployment defined in the deployments priority queue
        
        Returns True if deployment was successfully made and ships remain
    """
    ships = data["available_ships"]
    deployments = data["deployments"]
    
    # all deployments processed, return false
    if deployments.empty():
        return False
    
    # get next deployment
    score, target, num_ships = deployments.get()
    
    # loop until ship requirement met
    while num_ships > 0 and ships:
        # find closest planet with available ships
        closest_planet = None
        closest_planet_distance = inf
        for planet in ships.keys():
            planet_distance = state.distance(planet, target)
            if planet_distance < closest_planet_distance:
                closest_planet = planet
                closest_planet_distance = planet_distance
        
        # send ships
        fleet_size = min(planet.num_ships - 1, num_ships)
        issue_order(state, closest_planet, target, fleet_size)
        
        # reduce number of available ships
        num_ships -= fleet_size
        ships[closest_planet] -= fleet_size
        if ships[closest_planet] <= 0:
            del ships[closest_planet]
    
    # return true if ships still available
    return ships