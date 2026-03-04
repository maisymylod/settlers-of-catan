"""Settlers of Catan — Game logic server.

Handles board generation, resource distribution, dice rolling,
trading, building, and victory point tracking.
"""

import random
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from http.server import HTTPServer, SimpleHTTPRequestHandler


class Resource(Enum):
    WOOD = "wood"
    BRICK = "brick"
    SHEEP = "sheep"
    WHEAT = "wheat"
    ORE = "ore"


class BuildingType(Enum):
    SETTLEMENT = "settlement"
    CITY = "city"
    ROAD = "road"


# Cost to build each structure
BUILD_COSTS = {
    BuildingType.SETTLEMENT: {Resource.WOOD: 1, Resource.BRICK: 1, Resource.SHEEP: 1, Resource.WHEAT: 1},
    BuildingType.CITY: {Resource.WHEAT: 2, Resource.ORE: 3},
    BuildingType.ROAD: {Resource.WOOD: 1, Resource.BRICK: 1},
}

# Victory points per building
VICTORY_POINTS = {
    BuildingType.SETTLEMENT: 1,
    BuildingType.CITY: 2,
}

POINTS_TO_WIN = 10


@dataclass
class HexTile:
    """A single hexagonal tile on the board."""
    resource: Optional[Resource]
    number: int
    row: int
    col: int
    has_robber: bool = False

    def produces_on(self, roll: int) -> bool:
        return self.number == roll and not self.has_robber and self.resource is not None


@dataclass
class Player:
    """Represents a player in the game."""
    name: str
    color: str
    resources: dict = field(default_factory=lambda: {r: 0 for r in Resource})
    victory_points: int = 0
    settlements: list = field(default_factory=list)
    cities: list = field(default_factory=list)
    roads: list = field(default_factory=list)
    dev_cards: list = field(default_factory=list)
    has_longest_road: bool = False
    has_largest_army: bool = False
    knights_played: int = 0

    def total_resources(self) -> int:
        return sum(self.resources.values())

    def can_afford(self, building_type: BuildingType) -> bool:
        cost = BUILD_COSTS[building_type]
        return all(self.resources.get(r, 0) >= amount for r, amount in cost.items())

    def pay(self, building_type: BuildingType) -> None:
        cost = BUILD_COSTS[building_type]
        for resource, amount in cost.items():
            self.resources[resource] -= amount

    def add_resource(self, resource: Resource, amount: int = 1) -> None:
        self.resources[resource] = self.resources.get(resource, 0) + amount

    def calculate_vp(self) -> int:
        vp = len(self.settlements) * VICTORY_POINTS[BuildingType.SETTLEMENT]
        vp += len(self.cities) * VICTORY_POINTS[BuildingType.CITY]
        if self.has_longest_road:
            vp += 2
        if self.has_largest_army:
            vp += 2
        self.victory_points = vp
        return vp


class Board:
    """The Catan game board — generates and manages hex tiles."""

    LAYOUT = [3, 4, 5, 4, 3]  # Standard Catan board shape
    RESOURCE_DISTRIBUTION = (
        [Resource.WOOD] * 4 +
        [Resource.BRICK] * 3 +
        [Resource.SHEEP] * 4 +
        [Resource.WHEAT] * 4 +
        [Resource.ORE] * 3 +
        [None]  # Desert
    )
    NUMBER_TOKENS = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.tiles: list[HexTile] = []
        self._generate()

    def _generate(self) -> None:
        resources = list(self.RESOURCE_DISTRIBUTION)
        self.rng.shuffle(resources)

        numbers = list(self.NUMBER_TOKENS)
        self.rng.shuffle(numbers)

        number_idx = 0
        for row, count in enumerate(self.LAYOUT):
            for col in range(count):
                resource = resources.pop()
                if resource is None:
                    tile = HexTile(resource=None, number=0, row=row, col=col, has_robber=True)
                else:
                    tile = HexTile(resource=resource, number=numbers[number_idx], row=row, col=col)
                    number_idx += 1
                self.tiles.append(tile)

    def tiles_for_roll(self, roll: int) -> list[HexTile]:
        return [t for t in self.tiles if t.produces_on(roll)]

    def move_robber(self, row: int, col: int) -> None:
        for tile in self.tiles:
            tile.has_robber = False
        target = self.get_tile(row, col)
        if target:
            target.has_robber = True

    def get_tile(self, row: int, col: int) -> Optional[HexTile]:
        for tile in self.tiles:
            if tile.row == row and tile.col == col:
                return tile
        return None

    def to_dict(self) -> list[dict]:
        result = []
        for tile in self.tiles:
            result.append({
                "resource": tile.resource.value if tile.resource else "desert",
                "number": tile.number,
                "row": tile.row,
                "col": tile.col,
                "has_robber": tile.has_robber,
            })
        return result


class Dice:
    """Two six-sided dice."""

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.last_roll: tuple[int, int] = (0, 0)

    def roll(self) -> tuple[int, int]:
        d1 = self.rng.randint(1, 6)
        d2 = self.rng.randint(1, 6)
        self.last_roll = (d1, d2)
        return d1, d2

    @property
    def total(self) -> int:
        return sum(self.last_roll)

    @staticmethod
    def probability(number: int) -> float:
        """Probability of rolling a given total with 2d6."""
        if number < 2 or number > 12:
            return 0.0
        combos = 6 - abs(7 - number)
        return combos / 36.0


class TradeOffer:
    """Represents a trade proposal between players."""

    def __init__(self, proposer: Player, offering: dict, requesting: dict):
        self.proposer = proposer
        self.offering = offering   # {Resource: amount}
        self.requesting = requesting  # {Resource: amount}
        self.accepted = False

    def is_valid(self) -> bool:
        for resource, amount in self.offering.items():
            if self.proposer.resources.get(resource, 0) < amount:
                return False
        return True

    def execute(self, acceptor: Player) -> bool:
        if not self.is_valid():
            return False
        for resource, amount in self.requesting.items():
            if acceptor.resources.get(resource, 0) < amount:
                return False

        for resource, amount in self.offering.items():
            self.proposer.resources[resource] -= amount
            acceptor.resources[resource] = acceptor.resources.get(resource, 0) + amount

        for resource, amount in self.requesting.items():
            acceptor.resources[resource] -= amount
            self.proposer.resources[resource] = self.proposer.resources.get(resource, 0) + amount

        self.accepted = True
        return True


class Game:
    """Main game controller."""

    PLAYER_COLORS = ["#d64045", "#4a90d9", "#45a049", "#e8922f"]

    def __init__(self, player_names: list[str], seed: Optional[int] = None):
        if len(player_names) < 2 or len(player_names) > 4:
            raise ValueError("Game requires 2-4 players")

        self.board = Board(seed)
        self.dice = Dice(seed)
        self.players = [
            Player(name=name, color=self.PLAYER_COLORS[i])
            for i, name in enumerate(player_names)
        ]
        self.current_player_idx = 0
        self.turn_number = 0
        self.phase = "setup"
        self.winner: Optional[Player] = None
        self.log: list[str] = []

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    def roll_dice(self) -> tuple[int, int]:
        d1, d2 = self.dice.roll()
        total = d1 + d2
        self._log(f"{self.current_player.name} rolled {d1}+{d2}={total}")

        if total == 7:
            self._handle_seven()
        else:
            self._distribute_resources(total)

        return d1, d2

    def _distribute_resources(self, roll: int) -> None:
        producing_tiles = self.board.tiles_for_roll(roll)
        for tile in producing_tiles:
            for player in self.players:
                for pos in player.settlements:
                    if self._is_adjacent(pos, tile):
                        player.add_resource(tile.resource, 1)
                        self._log(f"{player.name} received 1 {tile.resource.value}")
                for pos in player.cities:
                    if self._is_adjacent(pos, tile):
                        player.add_resource(tile.resource, 2)
                        self._log(f"{player.name} received 2 {tile.resource.value}")

    def _handle_seven(self) -> None:
        for player in self.players:
            total = player.total_resources()
            if total > 7:
                discard_count = total // 2
                self._log(f"{player.name} must discard {discard_count} cards")

    def build(self, building_type: BuildingType, position: tuple) -> bool:
        player = self.current_player
        if not player.can_afford(building_type):
            return False

        player.pay(building_type)

        if building_type == BuildingType.SETTLEMENT:
            player.settlements.append(position)
        elif building_type == BuildingType.CITY:
            if position in player.settlements:
                player.settlements.remove(position)
            player.cities.append(position)
        elif building_type == BuildingType.ROAD:
            player.roads.append(position)

        self._log(f"{player.name} built a {building_type.value}")
        self._check_victory()
        return True

    def bank_trade(self, give: Resource, receive: Resource, ratio: int = 4) -> bool:
        player = self.current_player
        if player.resources.get(give, 0) < ratio:
            return False
        player.resources[give] -= ratio
        player.add_resource(receive, 1)
        self._log(f"{player.name} traded {ratio} {give.value} for 1 {receive.value}")
        return True

    def end_turn(self) -> None:
        self._log(f"{self.current_player.name} ended their turn")
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        self.turn_number += 1

    def _check_victory(self) -> None:
        for player in self.players:
            if player.calculate_vp() >= POINTS_TO_WIN:
                self.winner = player
                self._log(f"{player.name} wins with {player.victory_points} points!")

    def _is_adjacent(self, position: tuple, tile: HexTile) -> bool:
        """Check if a vertex position is adjacent to a hex tile."""
        pr, pc = position
        return abs(pr - tile.row) <= 1 and abs(pc - tile.col) <= 1

    def _log(self, message: str) -> None:
        self.log.append(f"[Turn {self.turn_number}] {message}")

    def state(self) -> dict:
        return {
            "board": self.board.to_dict(),
            "players": [
                {
                    "name": p.name,
                    "color": p.color,
                    "resources": {r.value: c for r, c in p.resources.items()},
                    "victory_points": p.calculate_vp(),
                    "settlements": len(p.settlements),
                    "cities": len(p.cities),
                    "roads": len(p.roads),
                }
                for p in self.players
            ],
            "current_player": self.current_player.name,
            "turn": self.turn_number,
            "phase": self.phase,
            "winner": self.winner.name if self.winner else None,
            "dice": list(self.dice.last_roll),
            "log": self.log[-10:],
        }


class GameRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves static files and a game API."""

    game: Optional[Game] = None

    def do_GET(self):
        if self.path == "/api/state":
            self._json_response(self.game.state() if self.game else {"error": "no game"})
        elif self.path == "/api/roll":
            if self.game:
                d1, d2 = self.game.roll_dice()
                self._json_response({"dice": [d1, d2], "total": d1 + d2})
            else:
                self._json_response({"error": "no game"})
        else:
            super().do_GET()

    def _json_response(self, data: dict) -> None:
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def run_server(player_names: list[str], port: int = 8000) -> None:
    """Start the game server."""
    game = Game(player_names)
    GameRequestHandler.game = game
    server = HTTPServer(("localhost", port), GameRequestHandler)
    print(f"Catan server running at http://localhost:{port}")
    print(f"Players: {', '.join(player_names)}")
    print(f"Board generated with {len(game.board.tiles)} tiles")
    server.serve_forever()


if __name__ == "__main__":
    run_server(["Alice", "Bob", "Charlie", "Diana"])
