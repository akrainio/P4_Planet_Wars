from timeit import default_timer as time


def check_ships_available(state, data, parameters):
    """
        Returns true if any ships are available
    """
    return data["available_ships"]


def check_time_remaining(state, data, parameters):
    """
        Returns true if a time amount specified in parameters remains in turn timer
    """
    return 1 - (time() - data["timer"]) >= parameters["time"]