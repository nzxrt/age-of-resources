"""
Центральное состояние игры. Все механики работают через этот модуль.
"""
import random

# Константы
PLAYER_ID = "player"
CAPTURE_COST = 150  # Ресурсов для захвата сектора
MINE_COST = 100     # Денег на постройку шахты
BED_COST = 50       # Денег на постройку грядки
MINE_PRODUCES = {"Камень": (2, 5), "Железная руда": (1, 3), "Уголь": (1, 4)}
BED_PRODUCES = {"Пшеница": (2, 4), "Морковь": (1, 3), "Картофель": (2, 5)}

# Биомы, на которых можно ставить шахту/грядки
MINE_BIOMES = ["Горы", "Лес"]
BED_BIOMES = ["Равнина", "Поле"]

# Соответствие ресурсов для торговли
RESOURCE_NAMES = {"Coal": "Уголь", "Iron": "Железо", "Iron_ore": "Железная руда", 
                  "Stone": "Камень", "Wood": "Дерево", "Wheat": "Пшеница", 
                  "Carrot": "Морковь", "Potato": "Картофель"}


class Country:
    """Страна — владелец территорий."""
    def __init__(self, country_id: str, name: str):
        self.id = country_id
        self.name = name
        self.territories = []
        self.inventory = {}
        self.balance = 15000 if country_id == PLAYER_ID else 500
        self.alliances = []
        self.wars = []
        self.is_player = country_id == PLAYER_ID

    def add_territory(self, territory_id: int, game_map):
        if territory_id not in self.territories:
            self.territories.append(territory_id)
            t = game_map.get_territory(territory_id)
            if t:
                t.set_owner(self.id)

    def remove_territory(self, territory_id: int, game_map):
        if territory_id in self.territories:
            self.territories.remove(territory_id)
            t = game_map.get_territory(territory_id)
            if t:
                t.set_owner(None)

    def get_bordering_country_ids(self, game_map, all_countries: dict):
        """Страны, чьи территории граничат с нашими."""
        bordering = set()
        for tid in self.territories:
            t = game_map.get_territory(tid)
            if not t:
                continue
            for nid in t.neighbors:
                nt = game_map.get_territory(nid)
                if nt and nt.owner and nt.owner != self.id:
                    bordering.add(nt.owner)
        return list(bordering)

    def add_resource(self, name: str, amount: int):
        self.inventory[name] = self.inventory.get(name, 0) + amount

    def remove_resource(self, name: str, amount: int) -> bool:
        cur = self.inventory.get(name, 0)
        if cur >= amount:
            self.inventory[name] = cur - amount
            if self.inventory[name] == 0:
                del self.inventory[name]
            return True
        return False

    def has_resource(self, name: str, amount: int = 1) -> bool:
        return self.inventory.get(name, 0) >= amount

    def spend_resources(self, amount: int) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False


class GameState:
    """Глобальное состояние игры."""
    def __init__(self, map_width=8, map_height=8):
        self.map_width = map_width
        self.map_height = map_height
        self.countries = {}
        self.player_country = None
        self.selected_sector_id = None
        self.game_started = False
        self.game_map = None  # Заполняется при инициализации карты

    def init_for_map(self, game_map):
        """Привязка к карте после её создания."""
        self.game_map = game_map

    def create_player_country(self, name: str, start_sector_id: int):
        """Создание страны игрока при выборе стартового сектора."""
        if self.player_country:
            return False
        c = Country(PLAYER_ID, name)
        self.countries[PLAYER_ID] = c
        c.add_territory(start_sector_id, self.game_map)
        self.player_country = c
        self.game_started = True
        return True

    def get_player_bordering_countries(self):
        if not self.player_country or not self.game_map:
            return []
        return self.player_country.get_bordering_country_ids(
            self.game_map, self.countries
        )

    def can_trade_with(self, country_id: str) -> bool:
        """Можно ли торговать со страной (граничит с нами)."""
        return country_id in self.get_player_bordering_countries()

    def get_adjacent_sectors(self, sector_id: int):
        """Соседние сектора."""
        t = self.game_map.get_territory(sector_id) if self.game_map else None
        if not t:
            return []
        return t.neighbors

    def can_capture_sector(self, sector_id: int) -> tuple[bool, str]:
        """Можно ли захватить сектор. Возвращает (ok, сообщение)."""
        if not self.player_country or not self.game_map:
            return False, "Игра не начата"
        t = self.game_map.get_territory(sector_id)
        if not t:
            return False, "Сектор не найден"
        if t.owner == PLAYER_ID:
            return False, "Сектор уже ваш"
        if t.owner and t.owner in self.player_country.alliances:
            return False, "Нельзя захватывать союзные территории"
        # Должен граничить с нашей территорией
        if sector_id not in self.get_adjacent_sectors_to_player():
            return False, "Сектор не граничит с вашей территорией"
        # Проверка ресурсов (используем баланс как "ресурсы" для простоты)
        if self.player_country.balance < CAPTURE_COST:
            return False, f"Нужно {CAPTURE_COST} ресурсов (баланс: {self.player_country.balance})"
        return True, ""

    def capture_sector(self, sector_id: int) -> tuple[bool, str]:
        ok, msg = self.can_capture_sector(sector_id)
        if not ok:
            return False, msg
        t = self.game_map.get_territory(sector_id)
        old_owner = t.owner
        if old_owner and old_owner in self.countries:
            self.countries[old_owner].remove_territory(sector_id, self.game_map)
        self.player_country.spend_resources(CAPTURE_COST)
        self.player_country.add_territory(sector_id, self.game_map)
        return True, f"Сектор {sector_id} захвачен!"

    def get_adjacent_sectors_to_player(self):
        """ID секторов, соседних с территориями игрока."""
        result = set()
        for tid in self.player_country.territories:
            result.update(self.get_adjacent_sectors(tid))
        return result - set(self.player_country.territories)

    def can_place_mine(self, sector_id: int) -> tuple[bool, str]:
        t = self.game_map.get_territory(sector_id) if self.game_map else None
        if not t or t.owner != PLAYER_ID:
            return False, "Сектор не принадлежит вам"
        biome = t.custom_data.get("biome", "") if t.custom_data else ""
        if biome not in MINE_BIOMES:
            return False, f"Шахту можно ставить только в {MINE_BIOMES}"
        if t.custom_data.get("building"):
            return False, "На секторе уже есть постройка"
        if self.player_country.balance < MINE_COST:
            return False, f"Нужно {MINE_COST} денег"
        return True, ""

    def can_place_bed(self, sector_id: int) -> tuple[bool, str]:
        t = self.game_map.get_territory(sector_id) if self.game_map else None
        if not t or t.owner != PLAYER_ID:
            return False, "Сектор не принадлежит вам"
        biome = t.custom_data.get("biome", "") if t.custom_data else ""
        if biome not in BED_BIOMES:
            return False, f"Грядки можно ставить только в {BED_BIOMES}"
        if t.custom_data.get("building"):
            return False, "На секторе уже есть постройка"
        if self.player_country.balance < BED_COST:
            return False, f"Нужно {BED_COST} денег"
        return True, ""

    def place_mine(self, sector_id: int) -> tuple[bool, str]:
        ok, msg = self.can_place_mine(sector_id)
        if not ok:
            return False, msg
        t = self.game_map.get_territory(sector_id)
        self.player_country.balance -= MINE_COST
        if not t.custom_data:
            t.custom_data = {}
        t.custom_data["building"] = "mine"
        return True, "Шахта построена!"

    def place_bed(self, sector_id: int) -> tuple[bool, str]:
        ok, msg = self.can_place_bed(sector_id)
        if not ok:
            return False, msg
        t = self.game_map.get_territory(sector_id)
        self.player_country.balance -= BED_COST
        if not t.custom_data:
            t.custom_data = {}
        t.custom_data["building"] = "bed"
        return True, "Грядки построены!"

    def extract_from_sector(self, sector_id: int) -> tuple[bool, str]:
        t = self.game_map.get_territory(sector_id) if self.game_map else None
        if not t or t.owner != PLAYER_ID:
            return False, "Сектор не принадлежит вам"
        b = t.custom_data.get("building") if t.custom_data else None
        if not b:
            return False, "На секторе нет шахты или грядок"
        if b == "mine":
            gathered = []
            for res, (lo, hi) in MINE_PRODUCES.items():
                amt = random.randint(lo, hi)
                self.player_country.add_resource(res, amt)
                gathered.append(f"{res}:{amt}")
            return True, f"Добыто из шахты: {', '.join(gathered)}"
        if b == "bed":
            gathered = []
            for res, (lo, hi) in BED_PRODUCES.items():
                amt = random.randint(lo, hi)
                self.player_country.add_resource(res, amt)
                gathered.append(f"{res}:{amt}")
            return True, f"Собрано с грядок: {', '.join(gathered)}"
        return False, "Неизвестная постройка"
