import heapq

class AStar:
    def __init__(self, game, max_expanded=100000):
     
        self.game = game
        self.expanded = 0
        self.max_expanded = max_expanded

        try:
            self.walls = {(x, y)
                          for y in range(self.game.height)
                          for x in range(self.game.width)
                          if self.game.map[y][x] == "#"}
        except Exception:
            
            self.walls = set()

    def heuristic(self, state):
        _, boxes = state
        h = 0
        for box in boxes:
            d = min(abs(box[0]-g[0]) + abs(box[1]-g[1]) for g in self.game.goals)
            h += d
        return h

    def _reconstruct_path(self, parent, goal_state):
        path = []
        cur = goal_state
        while True:
            prev, action = parent.get(cur, (None, None))
            if prev is None:
                break
            path.append(action)
            cur = prev
        path.reverse()
        return path

    def solve(self, start_state):
        player, boxes = start_state
        start = (player, frozenset(boxes))

        frontier = []
        g_scores = {start: 0}
        parent = {start: (None, None)}

        start_f = self.heuristic(start)
        heapq.heappush(frontier, (start_f, 0, start))

        while frontier:
            f, g, state = heapq.heappop(frontier)

            if g > g_scores.get(state, float("inf")):
                continue

            self.expanded += 1

            if self.game.is_goal(state):
                return self._reconstruct_path(parent, state)

            if self.expanded > self.max_expanded:
                break

            for succ_raw, action in self.game.get_successors(state):
                succ_player, succ_boxes_raw = succ_raw
                succ_boxes = frozenset(succ_boxes_raw)
                succ = (succ_player, succ_boxes)

                new_g = g + 1
                if new_g < g_scores.get(succ, float("inf")):
                    g_scores[succ] = new_g
                    parent[succ] = (state, action)
                    new_f = new_g + self.heuristic(succ)
                    heapq.heappush(frontier, (new_f, new_g, succ))

        return None
