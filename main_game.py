import os
import random
import pygame
from bots import GameMap, create_map_for_player
from game_state import (
    GameState, PLAYER_ID, Country,
    MINE_BIOMES, BED_BIOMES,
)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
MAP_WIDTH = 10
MAP_HEIGHT = 8

LEFT_PADDING = 50
RIGHT_PADDING = 320
BOTTOM_PADDING = 80

COLORS = {
    None: (80, 80, 80),
    PLAYER_ID: (0, 180, 80),
    "bot_0": (200, 50, 50),
    "bot_1": (50, 50, 200),
    "bot_2": (200, 150, 50),
}


def load_texture(path, default_size=(32, 32)):
    base = os.path.dirname(os.path.abspath(__file__))
    full = os.path.join(base, path)
    if os.path.exists(full):
        try:
            img = pygame.image.load(full)
            return pygame.transform.scale(img, default_size)
        except pygame.error:
            pass
    return None


def get_territory_at_pos(mouse_x, mouse_y, grid_start_x, grid_start_y, territory_size, map_width, map_height):
    rx = mouse_x - grid_start_x
    ry = mouse_y - grid_start_y
    if rx < 0 or ry < 0:
        return None
    col = rx // territory_size
    row = ry // territory_size
    if col >= map_width or row >= map_height:
        return None
    return row * map_width + col


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Age of Resources")

    font = pygame.font.Font(None, 22)
    font_large = pygame.font.Font(None, 28)
    clock = pygame.time.Clock()

    game_map = create_map_for_player(MAP_WIDTH, MAP_HEIGHT)

    ai_config = [
        ("bot_0", "Северная Империя", [1, 2]),
        ("bot_1", "Южная Лига", [MAP_WIDTH * (MAP_HEIGHT - 2), MAP_WIDTH * (MAP_HEIGHT - 2) + 1]),
        ("bot_2", "Восточный Союз", [MAP_WIDTH - 2, 2 * MAP_WIDTH - 2]),
    ]
    gs = GameState(MAP_WIDTH, MAP_HEIGHT)
    gs.init_for_map(game_map)
    for cid, name, sectors in ai_config:
        c = Country(cid, name)
        c.balance = 500
        gs.countries[cid] = c
        for sid in sectors:
            if 0 <= sid < MAP_WIDTH * MAP_HEIGHT:
                t = game_map.get_territory(sid)
                if t and (not t.custom_data or t.custom_data.get("biome") != "Море"):
                    c.add_territory(sid, game_map)

    try:
        bg = pygame.image.load("textures/maps/evu.jpg")
    except pygame.error:
        bg = None

    input_mode = "start"
    country_name_input = ""
    message_log = []
    selected_sector_id = None

    menu_mode = None
    menu_index = 0
    menu_sub = "main"
    menu_data = []
    trade_qty = 1
    trade_price = 50
    trade_selected_res = None
    RESOURCES_LIST = ["Coal", "Iron", "Stone", "Wood", "Wheat", "Carrot", "Potato"]
    DEFAULT_PRICES = {"Coal": 50, "Iron": 120, "Stone": 30, "Wood": 40, "Wheat": 25, "Carrot": 20, "Potato": 15}

    def add_msg(text):
        message_log.append(text)
        if len(message_log) > 5:
            message_log.pop(0)

    def open_trade_menu():
        nonlocal menu_mode, menu_index, menu_sub, menu_data
        bordering = gs.get_player_bordering_countries()
        if not bordering:
            add_msg("Нет соседних стран для торговли.")
            return
        menu_mode = "trade"
        menu_sub = "main"
        menu_index = 0
        menu_data = ["Продать", "Купить", "Выход (Esc)"]

    def open_war_menu():
        nonlocal menu_mode, menu_index, menu_sub, menu_data
        others = [(cid, gs.countries[cid].name) for cid in gs.countries if cid != PLAYER_ID]
        if not others:
            add_msg("Нет других стран.")
            return
        menu_mode = "war"
        menu_sub = "main"
        menu_index = 0
        menu_data = [f"{name} ({'Война' if cid in gs.player_country.wars else 'Мир'})" for cid, name in others]

    def open_alliance_menu():
        nonlocal menu_mode, menu_index, menu_sub, menu_data
        others = [(cid, gs.countries[cid].name) for cid in gs.countries if cid != PLAYER_ID]
        if not others:
            add_msg("Нет других стран.")
            return
        menu_mode = "alliance"
        menu_sub = "main"
        menu_index = 0
        menu_data = [f"{name} ({'Союзник' if cid in gs.player_country.alliances else '-'})" for cid, name in others]

    def handle_trade_confirm():
        nonlocal menu_mode, menu_sub, menu_index, menu_data, trade_qty, trade_price, trade_selected_res
        if menu_sub == "main":
            if menu_index == 0:
                inv = [(r, q) for r, q in gs.player_country.inventory.items() if q > 0]
                if not inv:
                    add_msg("Нет ресурсов для продажи.")
                    menu_mode = None
                    return
                menu_data = [f"{r}: {q} шт" for r, q in inv]
                menu_sub = "sell_res"
                menu_index = 0
            elif menu_index == 1:
                menu_data = RESOURCES_LIST + ["Назад"]
                menu_sub = "buy_res"
                menu_index = 0
            else:
                menu_mode = None
        elif menu_sub == "sell_res":
            inv = [(r, q) for r, q in gs.player_country.inventory.items() if q > 0]
            if inv and menu_index < len(inv):
                res, qty_max = inv[menu_index]
                trade_selected_res = res
                trade_qty = min(5, qty_max)
                trade_price = DEFAULT_PRICES.get(res, 50)
                menu_sub = "sell_qty"
                menu_data = [f"Кол-во: {trade_qty} (←→)", f"Цена: {trade_price}", "Подтвердить (Enter)"]
                menu_index = 0
            else:
                menu_mode = None
        elif menu_sub == "sell_qty":
            if trade_selected_res and gs.player_country.inventory.get(trade_selected_res, 0) >= trade_qty:
                if random.randint(1, 100) <= 60:
                    gs.player_country.balance += trade_price * trade_qty
                    gs.player_country.remove_resource(trade_selected_res, trade_qty)
                    add_msg(f"Продано {trade_qty} {trade_selected_res}. Баланс: {gs.player_country.balance}")
                else:
                    add_msg("Покупатель отказался.")
            menu_mode = None
        elif menu_sub == "buy_res":
            if menu_index < len(RESOURCES_LIST):
                res = RESOURCES_LIST[menu_index]
                trade_selected_res = res
                trade_price = DEFAULT_PRICES.get(res, 50)
                trade_qty = 1
                menu_sub = "buy_qty"
                menu_data = [f"Кол-во: {trade_qty} (←→)", f"Итого: {trade_price}", "Подтвердить (Enter)"]
                menu_index = 0
            else:
                menu_mode = None
        elif menu_sub == "buy_qty":
            if trade_selected_res:
                total = trade_price * trade_qty
                if gs.player_country.balance >= total and random.randint(1, 100) <= 60:
                    gs.player_country.balance -= total
                    gs.player_country.add_resource(trade_selected_res, trade_qty)
                    add_msg(f"Куплено {trade_qty} {trade_selected_res}. Баланс: {gs.player_country.balance}")
                else:
                    add_msg("Недостаточно средств или продавец отказался.")
            menu_mode = None

    def handle_war_confirm():
        nonlocal menu_mode
        others = [(cid, gs.countries[cid].name) for cid in gs.countries if cid != PLAYER_ID]
        if not others or menu_index >= len(others):
            menu_mode = None
            return
        cid, cname = others[menu_index]
        is_war = cid in gs.player_country.wars
        if is_war:
            gs.player_country.wars.remove(cid)
            gs.countries[cid].wars.remove(PLAYER_ID)
            add_msg(f"Мир заключён с {cname}.")
        else:
            gs.player_country.wars.append(cid)
            gs.countries[cid].wars.append(PLAYER_ID)
            add_msg(f"Война объявлена {cname}!")
        menu_mode = None

    def handle_alliance_confirm():
        nonlocal menu_mode
        others = [(cid, gs.countries[cid].name) for cid in gs.countries if cid != PLAYER_ID]
        if not others or menu_index >= len(others):
            menu_mode = None
            return
        cid, cname = others[menu_index]
        is_ally = cid in gs.player_country.alliances
        if is_ally:
            gs.player_country.alliances.remove(cid)
            gs.countries[cid].alliances.remove(PLAYER_ID)
            add_msg(f"Союз с {cname} расторгнут.")
        else:
            gs.player_country.alliances.append(cid)
            gs.countries[cid].alliances.append(PLAYER_ID)
            add_msg(f"Союз с {cname} заключён!")
        menu_mode = None

    def draw_menu_overlay():
        surf = pygame.Surface((500, 420))
        surf.fill((25, 30, 40))
        pygame.draw.rect(surf, (0, 120, 80), (0, 0, 500, 420), 3)
        x, y = 20, 20
        title = {"trade": "Торговля", "war": "Война / Мир", "alliance": "Союзы"}.get(menu_mode, "")
        txt = font_large.render(title, True, (0, 255, 150))
        surf.blit(txt, (x, y))
        y += 40
        hint = "↑↓ выбор  Enter подтвердить  Esc выход"
        if menu_sub in ("sell_qty", "buy_qty"):
            hint += "  ←→ кол-во"
        txt = font.render(hint, True, (150, 150, 150))
        surf.blit(txt, (x, y))
        y += 30
        for i, item in enumerate(menu_data[:15]):
            color = (0, 255, 150) if i == menu_index else (255, 255, 255)
            prefix = ">" if (menu_sub in ("sell_qty", "buy_qty") and i == 2) or (menu_sub not in ("sell_qty", "buy_qty") and i == menu_index) else " "
            txt = font.render(f"{prefix} {item}", True, color)
            surf.blit(txt, (x, y))
            y += 24
        screen.blit(surf, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 210))

    def draw_panel():
        x = SCREEN_WIDTH - RIGHT_PADDING + 10
        y = 20
        pygame.draw.rect(screen, (40, 40, 50), (SCREEN_WIDTH - RIGHT_PADDING, 0, RIGHT_PADDING, SCREEN_HEIGHT))

        if not gs.game_started:
            txt = font.render("Выберите сектор для старта", True, (255, 255, 255))
            screen.blit(txt, (x, y))
            y += 30
            txt = font.render("(клик по карте)", True, (180, 180, 180))
            screen.blit(txt, (x, y))
            return

        txt = font_large.render(f"{gs.player_country.name}", True, (0, 255, 150))
        screen.blit(txt, (x, y))
        y += 28
        txt = font.render(f"Баланс: {gs.player_country.balance}", True, (255, 255, 255))
        screen.blit(txt, (x, y))
        y += 24
        txt = font.render(f"Секторов: {len(gs.player_country.territories)}", True, (255, 255, 255))
        screen.blit(txt, (x, y))
        y += 30

        if selected_sector_id is not None:
            t = game_map.get_territory(selected_sector_id)
            if t:
                txt = font.render(f"Сектор {selected_sector_id}", True, (255, 220, 100))
                screen.blit(txt, (x, y))
                y += 22
                biome = t.custom_data.get("biome", "?") if t.custom_data else "?"
                txt = font.render(f"Биом: {biome}", True, (255, 255, 255))
                screen.blit(txt, (x, y))
                y += 22
                owner = t.owner or "Нейтральный"
                txt = font.render(f"Владелец: {owner}", True, (255, 255, 255))
                screen.blit(txt, (x, y))
                y += 30

                if t.owner == PLAYER_ID:
                    if not t.custom_data or not t.custom_data.get("building"):
                        if biome in MINE_BIOMES:
                            txt = font.render("[M] Шахта", True, (180, 255, 180))
                            screen.blit(txt, (x, y))
                            y += 22
                        if biome in BED_BIOMES:
                            txt = font.render("[G] Грядки", True, (180, 255, 180))
                            screen.blit(txt, (x, y))
                            y += 22
                    else:
                        txt = font.render("[E] Собрать ресурсы", True, (180, 255, 180))
                        screen.blit(txt, (x, y))
                        y += 22
                else:
                    ok, msg = gs.can_capture_sector(selected_sector_id)
                    if ok:
                        txt = font.render("[C] Захватить", True, (255, 200, 100))
                        screen.blit(txt, (x, y))
                        y += 22
                    else:
                        txt = font.render(msg[:35], True, (200, 150, 150))
                        screen.blit(txt, (x, y))
                        y += 22

        y += 20
        txt = font.render("[T] Торговля", True, (200, 200, 255))
        screen.blit(txt, (x, y))
        y += 22
        txt = font.render("[W] Война/Мир", True, (200, 200, 255))
        screen.blit(txt, (x, y))
        y += 22
        txt = font.render("[A] Союзы", True, (200, 200, 255))
        screen.blit(txt, (x, y))

        y = SCREEN_HEIGHT - 120
        for m in message_log[-3:]:
            txt = font.render(m[:45], True, (180, 220, 180))
            screen.blit(txt, (x, y))
            y += 20

    def draw_map_section():
        eff_w = SCREEN_WIDTH - LEFT_PADDING - RIGHT_PADDING
        eff_h = SCREEN_HEIGHT - BOTTOM_PADDING
        ts = min(eff_w // MAP_WIDTH, eff_h // MAP_HEIGHT)
        gw = MAP_WIDTH * ts
        gh = MAP_HEIGHT * ts
        gx = LEFT_PADDING + (eff_w - gw) // 2
        gy = (SCREEN_HEIGHT - BOTTOM_PADDING - gh) // 2

        if bg:
            scaled = pygame.transform.scale(bg, (gw, gh))
            screen.blit(scaled, (gx, gy))
        else:
            pygame.draw.rect(screen, (30, 50, 70), (gx, gy, gw, gh))

        for tid, t in game_map.territories.items():
            rx = gx + t.x * ts
            ry = gy + t.y * ts
            color = COLORS.get(t.owner, (60, 60, 60))
            if t.owner == PLAYER_ID:
                color = (0, 180, 80)
            elif t.owner:
                color = COLORS.get(t.owner, (100, 100, 120))
            pygame.draw.rect(screen, color, (rx, ry, ts, ts))
            pygame.draw.rect(screen, (255, 255, 255) if selected_sector_id == tid else (150, 150, 150), (rx, ry, ts, ts), 2)

            txt = font.render(f"s{tid}", True, (255, 255, 255))
            tr = txt.get_rect(center=(rx + ts // 2, ry + ts // 2 - 6))
            screen.blit(txt, tr)
            if t.custom_data and "biome" in t.custom_data:
                btxt = font.render(t.custom_data["biome"][:6], True, (200, 200, 200))
                br = btxt.get_rect(center=(rx + ts // 2, ry + ts // 2 + 8))
                screen.blit(btxt, br)
            if t.custom_data and t.custom_data.get("building"):
                sym = "M" if t.custom_data["building"] == "mine" else "B"
                btxt = font.render(sym, True, (255, 255, 0))
                screen.blit(btxt, (rx + 2, ry + 2))

        return gx, gy, ts

    running = True
    grid_gx = grid_gy = territory_size = 0

    while running:
        screen.fill((20, 20, 30))
        grid_gx, grid_gy, territory_size = draw_map_section()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                tid = get_territory_at_pos(event.pos[0], event.pos[1], grid_gx, grid_gy, territory_size, MAP_WIDTH, MAP_HEIGHT)
                if tid is not None:
                    if not gs.game_started:
                        t = game_map.get_territory(tid)
                        if t and t.custom_data and t.custom_data.get("biome") != "Море" and t.owner is None:
                            input_mode = "name"
                            selected_sector_id = tid
                            country_name_input = ""
                    else:
                        selected_sector_id = tid

            elif event.type == pygame.KEYDOWN:
                if input_mode == "name":
                    if event.key == pygame.K_RETURN and country_name_input.strip():
                        gs.create_player_country(country_name_input.strip(), selected_sector_id)
                        add_msg(f"Страна {country_name_input} создана!")
                        input_mode = "game"
                    elif event.key == pygame.K_BACKSPACE:
                        country_name_input = country_name_input[:-1]
                    elif event.unicode.isprintable():
                        country_name_input += event.unicode

                elif input_mode == "game" and gs.game_started:
                    if menu_mode:
                        if event.key == pygame.K_ESCAPE:
                            if menu_sub == "main":
                                menu_mode = None
                            else:
                                menu_sub = "main"
                                menu_index = 0
                                if menu_mode == "trade":
                                    menu_data = ["Продать", "Купить", "Выход (Esc)"]
                        elif event.key == pygame.K_UP:
                            menu_index = max(0, menu_index - 1)
                        elif event.key == pygame.K_DOWN:
                            menu_index = min(len(menu_data) - 1, menu_index + 1)
                        elif event.key == pygame.K_RETURN:
                            if menu_mode == "trade":
                                handle_trade_confirm()
                            elif menu_mode == "war":
                                handle_war_confirm()
                            elif menu_mode == "alliance":
                                handle_alliance_confirm()
                        elif menu_mode == "trade" and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                            if menu_sub == "sell_qty" and trade_selected_res:
                                qty_max = gs.player_country.inventory.get(trade_selected_res, 0)
                                if event.key == pygame.K_LEFT:
                                    trade_qty = max(1, trade_qty - 1)
                                else:
                                    trade_qty = min(min(99, qty_max), trade_qty + 1)
                                menu_data = [f"Кол-во: {trade_qty} (←→)", f"Цена: {trade_price}", "Подтвердить (Enter)"]
                            elif menu_sub == "buy_qty" and trade_selected_res:
                                if event.key == pygame.K_LEFT:
                                    trade_qty = max(1, trade_qty - 1)
                                else:
                                    max_qty = gs.player_country.balance // max(1, trade_price)
                                    trade_qty = min(99, max_qty, trade_qty + 1)
                                menu_data = [f"Кол-во: {trade_qty} (←→)", f"Итого: {trade_price * trade_qty}", "Подтвердить (Enter)"]
                    else:
                        if event.key == pygame.K_m and selected_sector_id is not None:
                            ok, msg = gs.place_mine(selected_sector_id)
                            add_msg(msg)
                        elif event.key == pygame.K_g and selected_sector_id is not None:
                            ok, msg = gs.place_bed(selected_sector_id)
                            add_msg(msg)
                        elif event.key == pygame.K_e and selected_sector_id is not None:
                            ok, msg = gs.extract_from_sector(selected_sector_id)
                            add_msg(msg)
                        elif event.key == pygame.K_c and selected_sector_id is not None:
                            ok, msg = gs.capture_sector(selected_sector_id)
                            add_msg(msg)
                        elif event.key == pygame.K_t and gs.game_started:
                            open_trade_menu()
                        elif event.key == pygame.K_w and gs.game_started:
                            open_war_menu()
                        elif event.key == pygame.K_a and gs.game_started:
                            open_alliance_menu()

        draw_panel()

        if menu_mode:
            draw_menu_overlay()

        if input_mode == "name":
            overlay = pygame.Surface((400, 80))
            overlay.fill((30, 40, 50))
            pygame.draw.rect(overlay, (0, 150, 100), (0, 0, 400, 80), 3)
            screen.blit(overlay, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 40))
            txt = font.render("Введите имя страны:", True, (255, 255, 255))
            screen.blit(txt, (SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 - 35))
            txt = font.render(country_name_input + "_", True, (0, 255, 150))
            screen.blit(txt, (SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 - 5))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run_game()
