from timeit import default_timer as time


def check_ships_available(state, data, parameters):
    return data["num_available_ships"] > 0


def check_time_remaining(state, data, parameters):
    return time() - data["timer"] >= parameters["time"]