import xml.etree.ElementTree as ET
import pygame
import os
from math import floor


def load_gif_frames(path):
    try:
        from PIL import Image
    except Exception:
        try:
            img = pygame.image.load(path).convert_alpha()
            return [img]
        except Exception:
            return []
    frames = []
    pil_img = Image.open(path)
    try:
        i = 0
        while True:
            pil_img.seek(i)
            frame = pil_img.convert("RGBA")
            data = frame.tobytes()
            size = frame.size
            py_image = pygame.image.fromstring(data, size, "RGBA")
            frames.append(py_image)
            i += 1
    except EOFError:
        pass
    if not frames:
        try:
            frames.append(pygame.image.load(path).convert_alpha())
        except:
            pass
    return frames


class Sokoban:
    def __init__(self, map_file, assets_dir="assets"):

        self.assets_dir = assets_dir
        self.map_file = map_file
        self.map, self.player, self.boxes, self.goals, self.width, self.height, self.tilewidth, self.tileheight = \
            self.load_map(map_file)

        self._load_assets()

    def load_map(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        width = int(root.attrib["width"])
        height = int(root.attrib["height"])
        tilewidth = int(root.attrib.get("tilewidth", 32))
        tileheight = int(root.attrib.get("tileheight", 32))

        
        gid_map = {}  
        for tileset in root.findall("tileset"):
            firstgid = int(tileset.attrib.get("firstgid", 0))
            source = tileset.attrib.get("source", "").lower()
            #
            if "wall" in source:
                gid_map["wall"] = firstgid
            elif "char" in source or "player" in source or "charactor" in source:
                gid_map["player"] = firstgid
            elif "box" in source:
                gid_map["box"] = firstgid
            elif "star" in source or "goal" in source or "checkpoint" in source:
                gid_map["goal"] = firstgid

        gid_map.setdefault("wall", gid_map.get("wall", 7))
        gid_map.setdefault("player", gid_map.get("player", 8))
        gid_map.setdefault("box", gid_map.get("box", 9))
        gid_map.setdefault("goal", gid_map.get("goal", 10))

        
        game_map = [[" " for _ in range(width)] for _ in range(height)]

        
        goals_set = set()

        
        for layer in root.findall("layer"):
            name = layer.attrib.get("name", "").lower()
            data_el = layer.find("data")
            if data_el is None or data_el.text is None:
                continue

            
            raw_data = data_el.text.strip().replace("\r", " ").replace("\n", " ")
            gids = [int(x) for x in raw_data.replace(" ", "").split(",") if x.strip() != ""]

            
            for y in range(height):
                for x in range(width):
                    gid = gids[y * width + x]
                    if gid == 0:
                        continue

                    
                    if name == "wall" or gid == gid_map.get("wall"):
                        game_map[y][x] = "#"

                    
                    if "checkpoint" in name or "goal" in name or gid == gid_map.get("goal"):
                        game_map[y][x] = "."
                        goals_set.add((x, y))

        player = None
        boxes = []
        

        
        for og in root.findall("objectgroup"):
            oname = og.attrib.get("name", "").lower()
            for obj in og.findall("object"):
                gid_attr = obj.attrib.get("gid")

                gid = int(gid_attr) if gid_attr is not None else None

                ox = float(obj.attrib.get("x", "0"))
                oy = float(obj.attrib.get("y", "0"))

                
                ty = int((oy - tileheight) // tileheight)
                tx = int(ox // tilewidth)

                
                if ty < 0:
                    ty = 0
                if tx < 0:
                    tx = 0
                if ty >= height:
                    ty = height - 1
                if tx >= width:
                    tx = width - 1

                
                if oname == "player" or (gid is not None and gid == gid_map["player"]):
                    player = (tx, ty)
                elif oname == "box" or (gid is not None and gid == gid_map["box"]):
                    boxes.append((tx, ty))

        
        for (gx, gy) in goals_set:
            
            game_map[gy][gx] = "."

        
        goals = sorted(list(goals_set))

        return game_map, player, boxes, goals, width, height, tilewidth, tileheight

    def _load_assets(self):
        def try_load(name_list):
            for nm in name_list:
                path = os.path.join(self.assets_dir, nm)
                if os.path.exists(path):
                    try:
                        return pygame.image.load(path).convert_alpha()
                    except:
                        try:
                            return pygame.image.load(path).convert()
                        except:
                            pass
            return None

        self.floor_img = try_load(["grass-2.png"])
        self.wall_img = try_load(["wall.png"])
        self.box_img = try_load(["box.png"])
        self.goal_img = try_load(["goal.png", "star.png", "checkpoint.png"])
        
        gif_candidates = ["charactor.gif", "player.gif", "char.gif"]
        gif_path = None
        for g in gif_candidates:
            p = os.path.join(self.assets_dir, g)
            if os.path.exists(p):
                gif_path = p
                break
        self.player_frames = load_gif_frames(gif_path) if gif_path else []

        
        for attr in ("floor_img", "wall_img", "box_img", "goal_img"):
            img = getattr(self, attr)
            if img:
                try:
                    setattr(self, attr, pygame.transform.scale(img, (self.tilewidth, self.tileheight)))
                except:
                    pass
        
        if self.player_frames:
            scaled = []
            for f in self.player_frames:
                try:
                    scaled.append(pygame.transform.scale(f, (self.tilewidth, self.tileheight)))
                except:
                    scaled.append(f)
            self.player_frames = scaled

    def is_goal(self, state):
        _, boxes = state
        return all(box in self.goals for box in boxes)

    def is_wall(self, x, y):
        return x < 0 or x >= self.width or y < 0 or y >= self.height or self.map[y][x] == "#"

    def is_deadlock_corner(self, boxes):
        for (bx, by) in boxes:
            if (bx, by) in self.goals:
                continue
            if self.is_wall(bx - 1, by) and self.is_wall(bx, by - 1):
                return True
            if self.is_wall(bx + 1, by) and self.is_wall(bx, by - 1):
                return True
            if self.is_wall(bx - 1, by) and self.is_wall(bx, by + 1):
                return True
            if self.is_wall(bx + 1, by) and self.is_wall(bx, by + 1):
                return True
        return False

    def all_boxes_blocked(self, boxes):
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for (bx, by) in boxes:
            for dx, dy in dirs:
                tx, ty = bx + dx, by + dy
                px, py = bx - dx, by - dy
                if not (0 <= tx < self.width and 0 <= ty < self.height): continue
                if not (0 <= px < self.width and 0 <= py < self.height): continue
                if self.map[ty][tx] == "#" or (tx, ty) in boxes: continue
                if self.map[py][px] == "#" or (px, py) in boxes: continue
                return False
        return True

    def is_reachable(self, start, target, boxes):
        from collections import deque
        visited = set([start])
        q = deque([start])
        while q:
            x, y = q.popleft()
            if (x, y) == target: return True
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.width and 0 <= ny < self.height): continue
                if self.map[ny][nx] == "#" or (nx, ny) in boxes: continue
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny))
        return False

    def get_successors(self, state):
        player, boxes = state
        successors = []
        dirs = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}
        boxes_set = set(boxes)
 
        for action, (dx, dy) in dirs.items():
            nx, ny = player[0] + dx, player[1] + dy

            if self.is_wall(nx, ny):
                continue

            new_boxes = list(boxes)

            if (nx, ny) in boxes_set:
                bx, by = nx + dx, ny + dy
                if self.is_wall(bx, by) or (bx, by) in boxes_set:
                    continue

                need_pos = (nx - dx, ny - dy)
                if not self.is_reachable(player, need_pos, boxes_set):
                    continue

                new_boxes.remove((nx, ny))
                new_boxes.append((bx, by))

            new_state = ((nx, ny), tuple(new_boxes))

            if self.is_deadlock_corner(new_state[1]):
                continue
            if self.all_boxes_blocked(new_state[1]):
                continue

            successors.append((new_state, action))

        return successors

    def get_start_state(self):
        return (self.player, tuple(self.boxes))

    def draw_state(self, screen, state, player_frame_index=0):
        player, boxes = state
        tw, th = self.tilewidth, self.tileheight
        for y in range(self.height):
            for x in range(self.width):
                px, py = x * tw, y * th
                if self.floor_img:
                    screen.blit(self.floor_img, (px, py))
                else:
                    pygame.draw.rect(screen, (200, 200, 200), (px, py, tw, th))

                c = self.map[y][x]
                if c == "#":
                    if self.wall_img:
                        screen.blit(self.wall_img, (px, py))
                    else:
                        pygame.draw.rect(screen, (100, 100, 100), (px, py, tw, th))
                elif c == ".":
                    if self.goal_img:
                        screen.blit(self.goal_img, (px, py))
                    else:
                        pygame.draw.rect(screen, (180, 220, 180), (px, py, tw, th))

        for bx, by in boxes:
            px, py = bx * tw, by * th
            if self.box_img:
                screen.blit(self.box_img, (px, py))
            else:
                pygame.draw.rect(screen, (165, 42, 42), (px, py, tw, th))

        px, py = player[0] * tw, player[1] * th
        if self.player_frames:
            idx = player_frame_index % len(self.player_frames)
            screen.blit(self.player_frames[idx], (px, py))
        else:
            pygame.draw.rect(screen, (0, 100, 255), (px, py, tw, th))

    def animate_solution(self, screen, solution, delay_ms=300):
        if solution is None:
            print("No solution (None).")
            return
        print("Solution (actions):", solution)

        clock = pygame.time.Clock()
        state = self.get_start_state()
        player_frame = 0

        screen_w = self.width * self.tilewidth
        screen_h = self.height * self.tileheight
        pygame.display.set_mode((screen_w, screen_h))

        self.draw_state(screen, state, player_frame)
        pygame.display.flip()
        pygame.time.wait(300)

        for action in solution:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return

            moved = False
            for succ, act in self.get_successors(state):
                if act == action or act.upper() == action.upper():
                    state = succ
                    moved = True
                    break
            if not moved:
                amap = {"UP": "U", "DOWN": "D", "LEFT": "L", "RIGHT": "R"}
                actkey = amap.get(action.upper(), action.upper())
                for succ, act in self.get_successors(state):
                    if act == actkey:
                        state = succ
                        break

            player_frame += 1

            self.draw_state(screen, state, player_frame)
            pygame.display.flip()

            t0 = pygame.time.get_ticks()
            while pygame.time.get_ticks() - t0 < delay_ms:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        return
                clock.tick(60)

        print("Animation finished.")
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return
            clock.tick(30)
