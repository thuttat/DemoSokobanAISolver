from collections import deque

class BFS:
    def __init__(self, game):
        self.game = game
        self.expanded = 0

    def encode_state(self, state):
        player, boxes = state
        return (player, tuple(sorted(boxes)))

    def solve(self, start_state):
        frontier = deque()
        frontier.append((start_state, []))
        explored = set()
        explored.add(self.encode_state(start_state))

        while frontier:
            state, path = frontier.popleft()
            self.expanded += 1

            if self.game.is_goal(state):
                return path

            for new_state, action in self.game.get_successors(state):
                encoded = self.encode_state(new_state)
                if encoded not in explored:
                    explored.add(encoded)
                    frontier.append((new_state, path + [action]))

        return None