class DFS:
    def __init__(self, game):
        self.game = game
        self.expanded = 0

    def encode_state(self, state):
        player, boxes = state
        return (player, tuple(sorted(boxes)))

    def solve(self, start_state, max_depth=200):
        stack = [(start_state, [])]
        explored = set()

        while stack:
            state, path = stack.pop()
            self.expanded += 1

            if self.game.is_goal(state):
                return path

            encoded = self.encode_state(state)
            if encoded in explored or len(path) > max_depth:
                continue
            explored.add(encoded)

            for new_state, action in self.game.get_successors(state):
                stack.append((new_state, path + [action]))

        return None