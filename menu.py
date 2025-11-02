import pygame
import sys
import os


ALGORITHMS = ["BFS", "DFS", "A*"]

def menu_loop(screen):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 40)

    
    level_images = []
    level_files = []
    for f in sorted(os.listdir("assets")):
        if f.startswith("level") or f.startswith("map") and f.endswith(".png"):
            img = pygame.image.load(os.path.join("assets", f)).convert()
            img = pygame.transform.scale(img, (300, 300))
            level_images.append(img)
            level_files.append(f.replace(".png", ".tmx"))
    if not level_images:
        print("Không tìm thấy level trong thư mục assets/")
        pygame.quit()
        sys.exit()

    level_index = 0
    algo_index = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    level_index = (level_index - 1) % len(level_images)
                elif event.key == pygame.K_RIGHT:
                    level_index = (level_index + 1) % len(level_images)
                elif event.key == pygame.K_SPACE:
                    algo_index = (algo_index + 1) % len(ALGORITHMS)
                elif event.key == pygame.K_RETURN:
                    
                    return level_files[level_index], ALGORITHMS[algo_index]

        
        screen.fill((30, 30, 30))

        
        title = font.render("SOKOBAN", True, (255, 255, 0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))

        
        preview = level_images[level_index]
        screen.blit(preview,
                    (screen.get_width() // 2 - preview.get_width() // 2 , 150))

        
        level_text = small_font.render(
            f"Level {level_index+1}/{len(level_images)}", True, (255, 255, 255)
        )
        screen.blit(level_text, (screen.get_width()//2 - level_text.get_width()//2, 470))

        
        algo_text = small_font.render(
            f"Algorithm: {ALGORITHMS[algo_index]}", True, (0, 200, 255)
        )
        screen.blit(algo_text, (screen.get_width()//2 - algo_text.get_width()//2, 520))

        pygame.display.flip()
        clock.tick(30)
