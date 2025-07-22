import pygame as pg
import sys
from pytmx.util_pygame import load_pygame

RES = WIDTH, HEIGHT = 320,320



class Tile(pg.sprite.Sprite):
    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = pg.transform.scale(image, (32, 32))
        self.rect = self.image.get_rect(topleft=pos)


class Player(pg.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = pg.transform.scale(image, (32, 32))
        self.rect = self.image.get_rect(topleft=pos)

class Box(pg.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = pg.transform.scale(image, (32, 32))
        self.rect = self.image.get_rect(topleft=pos)




class App:
    def __init__(self):
        pg.init()
        self.surface = pg.display.set_mode(RES)
        pg.display.set_caption("Map Example")
        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.map_data = load_pygame("maps/level_01.tmx")
        self.sprite_group = pg.sprite.Group()
        self.walls = pg.sprite.Group()

        self.checkpoints = pg.sprite.Group()

        for layer in self.map_data.visible_layers:
            if hasattr(layer, 'tiles'):
                for x, y, surf in layer.tiles():
                    pos = (x * 32, y * 32)
                    tile = Tile(surf, pos)
                    self.sprite_group.add(tile)

                    if layer.name == 'Checkpoint':
                        self.checkpoints.add(tile)


        for layer in self.map_data.visible_layers:
            print(f"LoadingLoading layer: {layer.name}")
            if hasattr(layer, 'tiles'):
                for x, y, surf in layer.tiles():
                    print(f"Tile at ({x}, {y}) has surface = {type(surf)}")
                    if isinstance(surf, pg.Surface):  
                        pos = (x * 32, y * 32)
                        if layer.name == 'Wall':
                            Tile(surf, pos, self.sprite_group, self.walls)
                        else:
                            Tile(surf, pos, self.sprite_group)


        print("TotalTotal:", len(self.sprite_group))

   
     
        self.player_img = pg.image.load("assets/charactor.png").convert_alpha()
        self.player = None

   
        for layer in self.map_data.layers:
            if layer.name == 'Player':
                for obj in layer:
                    print("Found object:", obj.name, obj.x, obj.y)
                    if obj.name == "Player":
                        px = int(obj.x)
                        py = int(obj.y - self.map_data.tileheight)
                        print("Loaded player at:", px, py)
                        self.player = Player(self.player_img, (px, py))

        self.box_img = pg.image.load("assets/box.png").convert_alpha()
        self.boxes = pg.sprite.Group()

        for layer in self.map_data.layers:
            if layer.name == 'Box':
                for obj in layer:
                    x, y = int(obj.x), int(obj.y - self.map_data.tileheight)
                    self.boxes.add(Tile(self.box_img, (x, y)))








    def draw(self):
        self.sprite_group.draw(self.surface)
        self.boxes.draw(self.surface)
        if self.player:
            self.surface.blit(self.player.image, self.player.rect)





    def run(self):
        while True:
            for e in pg.event.get():
                keys = pg.key.get_pressed()
                dx, dy = 0, 0
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_UP: self.move(0, -32)
                    elif e.key == pg.K_DOWN: self.move(0, 32)
                    elif e.key == pg.K_LEFT: self.move(-32, 0)
                    elif e.key == pg.K_RIGHT: self.move(32, 0)

                if dx != 0 or dy != 0:
                    new_rect = self.player.rect.move(dx, dy)
                    if not any(new_rect.colliderect(w.rect) for w in self.walls):
                        self.player.rect = new_rect
                    pg.time.wait(150)  

                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            self.surface.fill((0, 0, 0))  
            self.draw()

            self.delta_time = self.clock.tick()
            pg.display.set_caption("Map Example: " + str(round(self.clock.get_fps())))
            pg.display.flip()

    def move(self, dx, dy):
        next_rect = self.player.rect.move(dx, dy)

        # Va chạm với tường
        if any(next_rect.colliderect(w.rect) for w in self.walls):
            return

        # Va chạm với box
        for box in self.boxes:
            if next_rect.colliderect(box.rect):
                box_next = box.rect.move(dx, dy)

                if any(box_next.colliderect(w.rect) for w in self.walls) or \
                any(box_next.colliderect(b.rect) for b in self.boxes if b != box):
                    return

                box.rect = box_next
                break

        self.player.rect = next_rect

        if self.check_win():
            print("YOU WIN!")



    def check_win(self):
        for checkpoint in self.checkpoints:
            if not any(box.rect.colliderect(checkpoint.rect) for box in self.boxes):
                return False
        return True


if __name__ == '__main__':
    app = App()
    app.run()
