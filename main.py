import csv
import multiprocessing
import time
import pygame
import os

from menu import menu_loop
from sokoban import Sokoban

try:
    from algorithms.bfs import BFS
except Exception:
    BFS = None
try:
    from algorithms.dfs import DFS
except Exception:
    DFS = None
try:
    from algorithms.astar import AStar
except Exception:
    AStar = None


def show_text(screen, text, size=40):
    screen.fill((30, 30, 30))
    font = pygame.font.Font(None, size)
    surf = font.render(text, True, (255, 255, 255))
    screen.blit(surf, (screen.get_width()//2 - surf.get_width()//2,
                       screen.get_height()//2 - surf.get_height()//2))
    pygame.display.flip()


def run_solver_func(map_path, algo_name, result_queue):
    try:
        from sokoban import Sokoban
        from algorithms.bfs import BFS
        from algorithms.dfs import DFS
        from algorithms.astar import AStar

        game = Sokoban(map_path, assets_dir="assets")
        start = game.get_start_state()

        solver = None
        if algo_name.upper().startswith("BFS"):
            solver = BFS(game) if BFS is not None else None
        elif algo_name.upper().startswith("DFS"):
            solver = DFS(game) if DFS is not None else None
        elif algo_name.upper().startswith("A"):
            solver = AStar(game) if AStar is not None else None

        if solver is None:
            result_queue.put((None, 0))
            return

        if hasattr(solver, "solve"):
            result = solver.solve(start)
        elif callable(solver):
            result = solver(game, start)
        else:
            result = None

        expanded = getattr(solver, "expanded", 0)
        # gửi tuple về tiến trình chính
        result_queue.put((result, expanded))

    except Exception as e:
        print("Error in solver process:", e)
        try:
            result_queue.put((None, 0))
        except Exception:
            pass


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 650))
    pygame.display.set_caption("SOKOBAN")

    
    level_file, algo_name = menu_loop(screen)
    if not level_file:
        print("No level selected.")
        return

    
    if os.path.isabs(level_file) or level_file.startswith("maps"):
        map_path = level_file if os.path.exists(level_file) else os.path.join("maps", level_file)
    else:
        map_path = os.path.join("maps", level_file)

    if not os.path.exists(map_path):
        print("Map file not found:", map_path)
        return

    
    game = Sokoban(map_path, assets_dir="assets")

    show_text(screen, "WAITING...", size=48)
    pygame.event.pump()

    
    solver_stub = None
    if algo_name.upper().startswith("BFS") and BFS is not None:
        solver_stub = BFS(game)
    elif algo_name.upper().startswith("DFS") and DFS is not None:
        solver_stub = DFS(game)
    elif (algo_name.upper().startswith("A") or algo_name.upper().startswith("ASTAR")) and AStar is not None:
        solver_stub = AStar(game)
    else:
        try:
            mod = __import__("algorithms.bfs", fromlist=["bfs"])
            if hasattr(mod, "bfs"):
                solver_stub = lambda g: mod.bfs(g, game.get_start_state())
        except:
            pass

    if solver_stub is None:
        print("Không tìm thấy solver phù hợp. Kiểm tra thư mục algorithms/ và tên class.")
        return

    
    start_time = time.time()
    result_queue = multiprocessing.Queue()
    p = multiprocessing.Process(
        target=run_solver_func,
        args=(map_path, algo_name, result_queue)
    )
    p.start()
    p.join(timeout=900)  

    end_time = time.time()
    time_sec = round(end_time - start_time, 4)

    
    if p.is_alive():
        p.terminate()
        print("Timeout 15 minutes. Stop game.")
        show_text(screen, "Timeout 15 minutes. Stop game.", size=36)
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            pygame.time.Clock().tick(30)
        return

    
    if not result_queue.empty():
        data = result_queue.get()
    else:
        data = (None, 0)

    if isinstance(data, tuple) and len(data) == 2:
        solution, expanded_states = data
    else:
        solution, expanded_states = data, 0

    if solution is None:
        print("No solution.")
        success = 0
        solution_length = 0
    else:
        success = 1
        solution_length = len(solution)

    
    csv_file = "experiment_results.csv"
    write_header = not os.path.exists(csv_file)
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["map_name", "algo_name", "time_sec",
                             "solution_length", "expanded_states", "success"])
        writer.writerow([map_path, algo_name, time_sec,
                         solution_length, expanded_states, success])

    print("Result:", map_path, algo_name, "| Time:", time_sec,
          "| Steps:", solution_length, "| Expanded:", expanded_states,
          "|", "Success" if success else "Unsuccess")

    
    if solution:
        game.animate_solution(screen, solution, delay_ms=300)


if __name__ == "__main__":
    main()
