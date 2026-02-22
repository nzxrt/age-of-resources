import pygame
import random
from bots import Game, Territory, GameMap, Bot 


weight = 1920
height = 1080

COLORS = {
    None: (100, 100, 100),
    "bot_0": (255, 0, 0),
    "bot_1": (0, 0, 255),
    "bot_2": (0, 255, 0),
    "bot_3": (255, 255, 0),
    "bot_4": (255, 0, 255),
    "bot_5": (0, 255, 255),
}

LEFT_PADDING_PX = 60
RIGHT_PADDING_PX = 60
BOTTOM_PADDING_PX = 30

def draw_map(game, screen, font, background_image, territory_size, grid_start_x, grid_start_y, drawn_grid_width, drawn_grid_height):
    screen.fill((0, 0, 0))
    scaled_background = pygame.transform.scale(background_image, (drawn_grid_width, drawn_grid_height))
    screen.blit(scaled_background, (grid_start_x, grid_start_y))

    for territory_id, territory in game.game_map.territories.items():
        rect_x = grid_start_x + territory.x * territory_size
        rect_y = grid_start_y + territory.y * territory_size
        pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, territory_size, territory_size), 1)
        text_surface_id = font.render(f"s{territory.id}", True, (255, 255, 255))
        text_rect_id = text_surface_id.get_rect(center=(rect_x + territory_size // 2, rect_y + territory_size // 2 - 10))
        screen.blit(text_surface_id, text_rect_id)

        if territory.custom_data and "biome" in territory.custom_data:
            biome_name = territory.custom_data["biome"]
            text_surface_biome = font.render(biome_name, True, (255, 255, 255))
            text_rect_biome = text_surface_biome.get_rect(center=(rect_x + territory_size // 2, rect_y + territory_size // 2 + 10))
            screen.blit(text_surface_biome, text_rect_biome)

if __name__ == "__main__":
    pygame.init()

    MAP_WIDTH = 8
    MAP_HEIGHT = 8
    NUM_BOTS = 3
    TURNS_PER_SIMULATION = 50

    SCREEN_WIDTH = weight
    SCREEN_HEIGHT = height
    effective_drawable_width = SCREEN_WIDTH - LEFT_PADDING_PX - RIGHT_PADDING_PX
    effective_drawable_height = SCREEN_HEIGHT - BOTTOM_PADDING_PX
    
    TERRITORY_SIZE = min(effective_drawable_width // MAP_WIDTH, effective_drawable_height // MAP_HEIGHT)
    drawn_grid_width = MAP_WIDTH * TERRITORY_SIZE
    drawn_grid_height = MAP_HEIGHT * TERRITORY_SIZE
    grid_start_x = LEFT_PADDING_PX + (effective_drawable_width - drawn_grid_width) // 2
    grid_start_y = SCREEN_HEIGHT - BOTTOM_PADDING_PX - drawn_grid_height

    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Age of Resources")

    FONT = pygame.font.Font(None, 24)
    CLOCK = pygame.time.Clock()
    try:
        background_image = pygame.image.load('textures/maps/evu.jpg')
    except pygame.error as e:
        print(f"Не удалось загрузить изображение: {e}. Убедитесь, что 'textures/maps/evu.jpg' существует.")
        pygame.quit()
        exit()

    game = Game(num_bots=NUM_BOTS, map_width=MAP_WIDTH, map_height=MAP_HEIGHT)
    running = True
    current_turn_in_display = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if current_turn_in_display < TURNS_PER_SIMULATION:
                        game.run_turn()
                        current_turn_in_display += 1
                    else:
                        print("Симуляция завершена.")
                if event.key == pygame.K_ESCAPE:
                    running = False

        draw_map(game, SCREEN, FONT, background_image, TERRITORY_SIZE, grid_start_x, grid_start_y, drawn_grid_width, drawn_grid_height)

        pygame.display.flip()
        CLOCK.tick(60)

    pygame.quit()