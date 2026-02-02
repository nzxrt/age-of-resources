import pygame
import random
from bots import Game, Territory, GameMap, Bot 


weight = 1920
height = 1080

# Цвета для отрисовки
COLORS = {
    None: (100, 100, 100),  # Серый для нейтральных территорий
    "bot_0": (255, 0, 0),   # Красный
    "bot_1": (0, 0, 255),   # Синий
    "bot_2": (0, 255, 0),   # Зеленый
    "bot_3": (255, 255, 0), # Желтый
    "bot_4": (255, 0, 255), # Фиолетовый
    "bot_5": (0, 255, 255), # Голубой
}

# Параметры отступов для сетки территорий
LEFT_PADDING_PX = 60
RIGHT_PADDING_PX = 60
BOTTOM_PADDING_PX = 30

def draw_map(game, screen, font, background_image, territory_size, grid_start_x, grid_start_y, drawn_grid_width, drawn_grid_height):
    screen.fill((0, 0, 0))  # Черный фон для всего экрана
    scaled_background = pygame.transform.scale(background_image, (drawn_grid_width, drawn_grid_height))#трансформация размеров
    # Отрисовываем масштабированный фон в позиции начала сетки
    screen.blit(scaled_background, (grid_start_x, grid_start_y))

    for territory_id, territory in game.game_map.territories.items():
        # Вычисляем позицию на экране с учетом отступов
        rect_x = grid_start_x + territory.x * territory_size
        rect_y = grid_start_y + territory.y * territory_size
        
        # Отрисовываем границу 
        pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, territory_size, territory_size), 1) # Белая граница

        # Выводим название сектора (s0, s1, s2...)
        text_surface_id = font.render(f"s{territory.id}", True, (255, 255, 255)) # Белый текст
        text_rect_id = text_surface_id.get_rect(center=(rect_x + territory_size // 2, rect_y + territory_size // 2 - 10)) # Центрируем ID чуть выше
        screen.blit(text_surface_id, text_rect_id)

        # Выводим название биома
        if territory.custom_data and "biome" in territory.custom_data:
            biome_name = territory.custom_data["biome"]
            text_surface_biome = font.render(biome_name, True, (255, 255, 255)) # Белый текст для биома
            text_rect_biome = text_surface_biome.get_rect(center=(rect_x + territory_size // 2, rect_y + territory_size // 2 + 10)) # Центрируем биом чуть ниже ID
            screen.blit(text_surface_biome, text_rect_biome)

# Пример использования
if __name__ == "__main__":
    pygame.init()

    MAP_WIDTH = 8
    MAP_HEIGHT = 8
    NUM_BOTS = 3
    TURNS_PER_SIMULATION = 50 # Увеличиваем количество ходов для более наглядной симуляции

    SCREEN_WIDTH = weight # Используем твою ширину
    SCREEN_HEIGHT = height # Используем твою высоту

    # Расчет эффективной области для сетки карты с учетом отступов
    effective_drawable_width = SCREEN_WIDTH - LEFT_PADDING_PX - RIGHT_PADDING_PX
    effective_drawable_height = SCREEN_HEIGHT - BOTTOM_PADDING_PX
    
    TERRITORY_SIZE = min(effective_drawable_width // MAP_WIDTH, effective_drawable_height // MAP_HEIGHT)
    drawn_grid_width = MAP_WIDTH * TERRITORY_SIZE
    drawn_grid_height = MAP_HEIGHT * TERRITORY_SIZE

    # Рассчитываем начальные координаты для отрисовки сетки
    # Горизонтальное центрирование с учетом левого и правого отступов
    grid_start_x = LEFT_PADDING_PX + (effective_drawable_width - drawn_grid_width) // 2
    # Вертикальное позиционирование с учетом нижнего отступа
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

    game = Game(num_bots=NUM_BOTS, map_width=MAP_WIDTH, map_height=MAP_HEIGHT) # Изменить данные

    # Игровой цикл Pygame
    running = True
    current_turn_in_display = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Нажмите пробел для следующего хода
                    if current_turn_in_display < TURNS_PER_SIMULATION:
                        game.run_turn()
                        current_turn_in_display += 1
                    else:
                        print("Симуляция завершена.")
                if event.key == pygame.K_ESCAPE: # Нажмите ESC для выхода
                    running = False

        # Отрисовка карты
        draw_map(game, SCREEN, FONT, background_image, TERRITORY_SIZE, grid_start_x, grid_start_y, drawn_grid_width, drawn_grid_height)

        pygame.display.flip()
        CLOCK.tick(60) # Ограничиваем FPS

    pygame.quit()