#!/usr/bin/env python
#

import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Leaf, RepeatUntilFail

from planet_wars import PlanetWars, finish_turn

# You have to improve this tree or create an entire new one that is capable of winning against all the 5 opponent bots
def setup_behavior_tree():
    # Top-down construction of behavior tree
    root = Sequence(name="Root")
    
    startup_sequence = Sequence(child_nodes=[Leaf(start_timer), Leaf(initialize_ships_and_deployments), Leaf(find_focus_point),
                                             Leaf(create_dist_table)], name="Startup Sequence")
    
    defense = Leaf(defense_strategy)
    offense = Leaf(offense_strategy)
    
    deploy_loop = RepeatUntilFail(child_node=Leaf(deploy_fleet), name="Deployment Loop")
    
    root.child_nodes = [ startup_sequence, defense, offense, deploy_loop ]

    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
