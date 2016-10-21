from copy import deepcopy
import logging


def log_execution(fn):
    def logged_fn(self, state, data={}):
        logging.debug('Executing:' + str(self))
        result = fn(self, state, data)
        logging.debug('Result: ' + str(self) + ' -> ' + ('Success' if result else 'Failure'))
        return result
    return logged_fn


############################### Base Classes ##################################
class Node:
    def __init__(self):
        raise NotImplementedError

    def execute(self, state, data={}):
        raise NotImplementedError

    def copy(self):
        return deepcopy(self)


class Composite(Node):
    def __init__(self, child_nodes=[], name=None):
        self.child_nodes = child_nodes
        self.name = name

    def execute(self, state, data={}):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.name if self.name else ''

    def tree_to_string(self, indent=0):
        string = '| ' * indent + str(self) + '\n'
        for child in self.child_nodes:
            if hasattr(child, 'tree_to_string'):
                string += child.tree_to_string(indent + 1)
            else:
                string += '| ' * (indent + 1) + str(child) + '\n'
        return string


class Decorator(Node):
    def __init__(self, child_node=None, name=None):
        self.child_node = child_node
        self.name = name
    
    def execute(self, state, data={}):
        raise NotImplementedError
    
    def __str__(self):
        return self.__class__.__name__ + ': ' + self.name if self.name else ''

    def tree_to_string(self, indent=0):
        string = '| ' * indent + str(self) + '\n'
        if hasattr(self.child_node, 'tree_to_string'):
            string += self.child_node.tree_to_string(indent + 1)
        else:
            string += '| ' * (indent + 1) + str(self.child_node) + '\n'
        return string


############################### Composite Nodes ##################################
class Selector(Composite):
    @log_execution
    def execute(self, state, data={}):
        for child_node in self.child_nodes:
            success = child_node.execute(state, data)
            if success:
                return True
        else:  # for loop completed without success; return failure
            return False


class Sequence(Composite):
    @log_execution
    def execute(self, state, data={}):
        for child_node in self.child_nodes:
            continue_execution = child_node.execute(state, data)
            if not continue_execution:
                return False
        else:  # for loop completed without failure; return success
            return True


############################### Leaf Nodes ##################################
class Leaf(Node):
    def __init__(self, function, parameters={}):
        self.function = function
        self.parameters = parameters

    @log_execution
    def execute(self, state, data={}):
        return self.function(state, data, self.parameters)

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.function.__name__


############################### Decorator Nodes ##################################
class Inverter(Decorator):
    @log_execution
    def execute(self, state, data):
        return not self.child_node.execute(state, data)
        

class Succeeder(Decorator):
    @log_execution
    def execute(self, state, data={}):
        self.child_node.execute(state, data)
        return True
        
class RepeatUntilFail(Decorator):
    @log_execution
    def execute(self, state, data={}):
        while self.child_node.execute(state, data):
            continue
        return True