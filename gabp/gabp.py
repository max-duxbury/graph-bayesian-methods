"""
Defines the classes for variable nodes, factor nodes and edges, and the factor graph as a whole.
"""

import numpy as np
import scipy.linalg

class FactorGraph:
    def __init__(self) -> None:
        pass

class VariableNode:
    def __init__(self, variable_id) -> None:
        self.variable_id = variable_id
        self.adj_factors = []

    def update_belief(self) -> None:
        """
        Variable node beliefs are updated by taking the product of the incoming messages 
        from all adjacent factors, each of which represents that factor's belief on the 
        recieving node's variables. 
        """
        pass

class Factor:
    def __init__(self) -> None:
        pass
