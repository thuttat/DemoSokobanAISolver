class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0 if parent is None else parent.depth + 1

    def expand(self, problem):
        return [
            Node(next_state, self, action, self.path_cost + cost)
            for (next_state, action, cost) in problem.successor(self.state)
        ]

    def solution(self):
        node, path = self, []
        while node and node.action:
            path.append(node.action)
            node = node.parent
        return list(reversed(path))


class Problem:
    def __init__(self, initial, goal):
        self.initial = initial
        self.goal = goal

    def successor(self, state):
        raise NotImplementedError

    def goal_test(self, state):
        return state == self.goal

    def h(self, state):
        return 0  
