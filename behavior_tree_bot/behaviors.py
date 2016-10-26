import sys, logging, inspect, os
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

sys.path.insert(0, '../')
from planet_wars import issue_order
from math import inf, sqrt
from timeit import default_timer as time
from queue import PriorityQueue

defense_weight = 0
offense_weight = 100
offense_overkill = 10


def dist(x0, y0, x1, y1):
    """
        2D distance function
    """
    return sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)


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
    data["num_available_ships"] = 0
    data["available_ships"] = {}
    data["deployments"] = PriorityQueue()

    # find available ships
    for planet in state.my_planets():
        if planet.num_ships > 1:
            data["num_available_ships"] += planet.num_ships - 1
            data["available_ships"][planet] = planet.num_ships - 1
    return True


def create_dist_table(state, data, parameters):
    """
        Creates a table that stores average distances between each planet and all other planets
        Used in the offensive strategy to calculate the clustered-ness of a planet when finding the long term value
        Doesn't account for the starting planets for simplicity's sake
    """
    data["dist_table"] = {}
    for planet in state.not_my_planets():
        quality = 0
        num_planets = 0
        dist_sum = 0

        def calc_dists(num_planets, dist_sum):
            num_planets += 1
            this_dist = 0
            if planet != other_planet:
                this_dist = dist(planet.x, other_planet.x, planet.y, other_planet.y)
                if this_dist <= 10:
                    dist_sum += this_dist
            return this_dist, num_planets, dist_sum

        for other_planet in state.neutral_planets():
            this_dist, num_planets, dist_sum = calc_dists(num_planets, dist_sum)

        for other_planet in state.my_planets():
            this_dist, num_planets, dist_sum = calc_dists(num_planets, dist_sum)

        for other_planet in state.enemy_planets():
            this_dist, num_planets, dist_sum = calc_dists(num_planets, dist_sum)

        data["dist_table"][planet] = dist_sum / num_planets
    return True


def find_focus_point(state, data, parameters):
    """
        Finds the central point of our currently held planets
        Used to estimate distances when gauging targets
        Calculation could be adjusted to prioritize planets differently
    """
    data["focus_x"] = 0
    data["focus_y"] = 0
    if len(state.my_planets()) > 0:
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
    deployments = data["deployments"]
    for enemy_fleet in state.enemy_fleets():
        planet = state.planets[enemy_fleet.destination_planet]
        if planet.owner == 1:
            score = defense_weight + dist(data["focus_x"], planet.x, data["focus_y"], planet.y)
            logging.info('\n' + "Defensive score: " + score.__str__())
            deployments.put((score, planet, enemy_fleet.num_ships))
    return True


def offense_strategy(state, data, parameters):
    deployments = data["deployments"]
    for planet in state.not_my_planets():
        num_ships = planet.num_ships + 1
        if planet.owner == 2:
            num_ships += dist(data["focus_x"], planet.x, data["focus_y"],
                              planet.y) * planet.growth_rate + offense_overkill
        score = offense_weight + dist(data["focus_x"], planet.x, data["focus_y"],
                                      planet.y) - planet.growth_rate + num_ships


        score = offense_weight + dist(data["focus_x"], planet.x, data["focus_y"],
                                      planet.y) - planet.growth_rate + num_ships + data["dist_table"][planet]

        deployments.put((score, planet, num_ships))
        logging.info('\n' + "Offensive score: " + score.__str__())
    return True


def deploy_fleet(state, data, parameters):
    """
        Attempts to make a deployment defined in the deployments priority queue
        
        Returns True if deployment was successfully made
    """
    ships = data["available_ships"]
    deployments = data["deployments"]

    # all deployments processed, return false
    if deployments.empty():
        return False

    # get next deployment
    score, target, num_ships = deployments.get()

    if num_ships > data["num_available_ships"]:
        return False

    # account for fleets already sent
    for fleet in state.my_fleets():
        if fleet.destination_planet == target.ID:
            num_ships -= fleet.num_ships

    # account for ships on planet
    if target in ships:
        ships_on_planet = min(num_ships, ships[target])
        num_ships -= ships_on_planet
        ships[target] -= ships_on_planet
        data["num_available_ships"] -= ships_on_planet
        if ships[target] <= 0:
            ships.pop(target)

    # loop until ship requirement met
    while num_ships > 0 and ships:
        # find closest planet with available ships
        closest_planet = None
        closest_planet_distance = inf
        for planet in ships.keys():
            planet_distance = state.distance(planet.ID, target.ID)
            if planet_distance < closest_planet_distance:
                closest_planet = planet
                closest_planet_distance = planet_distance

        # send ships
        fleet_size = min(ships[closest_planet], num_ships)
        issue_order(state, closest_planet.ID, target.ID, fleet_size)

        # reduce number of available ships
        num_ships -= fleet_size
        data["num_available_ships"] -= fleet_size
        ships[closest_planet] -= fleet_size
        if ships[closest_planet] <= 0:
            ships.pop(closest_planet)

    return True
