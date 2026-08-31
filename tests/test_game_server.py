"""Tests for the Catan game logic.

Everything here is seeded, so the suite is deterministic.
"""

import pathlib
import sys
from collections import Counter

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from game_server import (  # noqa: E402
    BUILD_COSTS,
    POINTS_TO_WIN,
    Board,
    BuildingType,
    Dice,
    Game,
    HexTile,
    Player,
    Resource,
    TradeOffer,
)


class TestBoard:
    def test_has_the_standard_nineteen_tiles(self):
        assert len(Board(seed=1).tiles) == sum(Board.LAYOUT) == 19

    def test_resource_counts_match_the_standard_game(self):
        counts = Counter(t.resource for t in Board(seed=1).tiles)
        assert counts[Resource.WOOD] == 4
        assert counts[Resource.SHEEP] == 4
        assert counts[Resource.WHEAT] == 4
        assert counts[Resource.BRICK] == 3
        assert counts[Resource.ORE] == 3
        assert counts[None] == 1  # the desert

    def test_every_producing_tile_gets_a_number_and_the_desert_does_not(self):
        for tile in Board(seed=7).tiles:
            if tile.resource is None:
                assert tile.number == 0
            else:
                assert 2 <= tile.number <= 12
                assert tile.number != 7  # 7 moves the robber, it is never a token

    def test_the_number_tokens_are_the_standard_multiset(self):
        numbers = sorted(t.number for t in Board(seed=3).tiles if t.resource is not None)
        assert numbers == sorted(Board.NUMBER_TOKENS)

    def test_the_robber_starts_on_the_desert_and_only_there(self):
        tiles = Board(seed=5).tiles
        robbers = [t for t in tiles if t.has_robber]
        assert len(robbers) == 1
        assert robbers[0].resource is None

    def test_the_same_seed_gives_the_same_board(self):
        a, b = Board(seed=42).to_dict(), Board(seed=42).to_dict()
        assert a == b

    def test_different_seeds_give_different_boards(self):
        assert Board(seed=1).to_dict() != Board(seed=2).to_dict()

    def test_tiles_for_roll_skips_the_robbed_tile(self):
        board = Board(seed=11)
        target = next(t for t in board.tiles if t.resource is not None)
        board.move_robber(target.row, target.col)
        assert target not in board.tiles_for_roll(target.number)

    def test_moving_the_robber_leaves_exactly_one_behind(self):
        board = Board(seed=13)
        board.move_robber(2, 2)
        assert sum(1 for t in board.tiles if t.has_robber) == 1
        assert board.get_tile(2, 2).has_robber

    def test_get_tile_returns_none_off_the_board(self):
        assert Board(seed=1).get_tile(99, 99) is None


class TestHexTile:
    def test_produces_on_its_own_number(self):
        assert HexTile(Resource.WOOD, 8, 0, 0).produces_on(8)

    def test_does_not_produce_on_another_number(self):
        assert not HexTile(Resource.WOOD, 8, 0, 0).produces_on(5)

    def test_the_robber_blocks_production(self):
        assert not HexTile(Resource.WOOD, 8, 0, 0, has_robber=True).produces_on(8)

    def test_the_desert_never_produces(self):
        assert not HexTile(None, 0, 0, 0).produces_on(0)


class TestDice:
    def test_both_dice_stay_in_range(self):
        dice = Dice(seed=1)
        for _ in range(200):
            d1, d2 = dice.roll()
            assert 1 <= d1 <= 6 and 1 <= d2 <= 6

    def test_total_matches_the_last_roll(self):
        dice = Dice(seed=1)
        d1, d2 = dice.roll()
        assert dice.total == d1 + d2

    def test_the_same_seed_gives_the_same_sequence(self):
        a = [Dice(seed=99).roll() for _ in range(5)]
        b = [Dice(seed=99).roll() for _ in range(5)]
        assert a == b

    @pytest.mark.parametrize(
        "number,combos",
        [(2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 5), (9, 4), (10, 3), (11, 2), (12, 1)],
    )
    def test_probability_matches_the_2d6_distribution(self, number, combos):
        assert Dice.probability(number) == pytest.approx(combos / 36)

    def test_the_whole_distribution_sums_to_one(self):
        assert sum(Dice.probability(n) for n in range(2, 13)) == pytest.approx(1.0)

    @pytest.mark.parametrize("number", [0, 1, 13, -5])
    def test_impossible_totals_have_zero_probability(self, number):
        assert Dice.probability(number) == 0.0


class TestPlayer:
    def test_starts_with_no_resources(self):
        assert Player("A", "red").total_resources() == 0

    def test_cannot_afford_anything_when_empty(self):
        player = Player("A", "red")
        for building in BUILD_COSTS:
            assert not player.can_afford(building)

    def test_can_afford_once_the_exact_cost_is_held(self):
        player = Player("A", "red")
        for resource, amount in BUILD_COSTS[BuildingType.SETTLEMENT].items():
            player.add_resource(resource, amount)
        assert player.can_afford(BuildingType.SETTLEMENT)

    def test_one_resource_short_is_not_affordable(self):
        player = Player("A", "red")
        cost = BUILD_COSTS[BuildingType.CITY]
        for resource, amount in cost.items():
            player.add_resource(resource, amount)
        player.resources[Resource.ORE] -= 1
        assert not player.can_afford(BuildingType.CITY)

    def test_paying_deducts_exactly_the_cost(self):
        player = Player("A", "red")
        for resource in Resource:
            player.add_resource(resource, 5)
        player.pay(BuildingType.CITY)
        assert player.resources[Resource.WHEAT] == 3
        assert player.resources[Resource.ORE] == 2
        assert player.resources[Resource.WOOD] == 5  # untouched

    def test_victory_points_count_settlements_and_cities(self):
        player = Player("A", "red")
        player.settlements = [(0, 0), (1, 1)]
        player.cities = [(2, 2)]
        assert player.calculate_vp() == 2 * 1 + 1 * 2

    def test_longest_road_and_largest_army_are_worth_two_each(self):
        player = Player("A", "red")
        player.has_longest_road = True
        player.has_largest_army = True
        assert player.calculate_vp() == 4

    def test_calculate_vp_writes_back_to_the_field(self):
        player = Player("A", "red")
        player.cities = [(0, 0)]
        player.calculate_vp()
        assert player.victory_points == 2


class TestTradeOffer:
    def _stocked(self):
        player = Player("A", "red")
        player.add_resource(Resource.WOOD, 3)
        return player

    def test_valid_when_the_proposer_holds_what_it_offers(self):
        offer = TradeOffer(self._stocked(), {Resource.WOOD: 2}, {Resource.ORE: 1})
        assert offer.is_valid()

    def test_invalid_when_offering_more_than_held(self):
        offer = TradeOffer(self._stocked(), {Resource.WOOD: 99}, {Resource.ORE: 1})
        assert not offer.is_valid()

    def test_execute_moves_resources_both_ways(self):
        proposer = self._stocked()
        acceptor = Player("B", "blue")
        acceptor.add_resource(Resource.ORE, 2)
        offer = TradeOffer(proposer, {Resource.WOOD: 2}, {Resource.ORE: 1})
        assert offer.execute(acceptor)
        assert proposer.resources[Resource.WOOD] == 1
        assert proposer.resources[Resource.ORE] == 1
        assert acceptor.resources[Resource.WOOD] == 2
        assert acceptor.resources[Resource.ORE] == 1

    def test_execute_fails_when_the_acceptor_cannot_pay(self):
        proposer = self._stocked()
        acceptor = Player("B", "blue")  # holds nothing
        offer = TradeOffer(proposer, {Resource.WOOD: 2}, {Resource.ORE: 1})
        assert not offer.execute(acceptor)
        assert proposer.resources[Resource.WOOD] == 3  # unchanged


class TestGame:
    def test_creates_a_player_per_name(self):
        game = Game(["A", "B", "C"], seed=1)
        assert [p.name for p in game.players] == ["A", "B", "C"]

    def test_starts_on_the_first_player(self):
        assert Game(["A", "B"], seed=1).current_player.name == "A"

    def test_end_turn_advances_and_wraps(self):
        game = Game(["A", "B"], seed=1)
        game.end_turn()
        assert game.current_player.name == "B"
        game.end_turn()
        assert game.current_player.name == "A"

    def test_rolling_returns_two_dice_in_range(self):
        d1, d2 = Game(["A", "B"], seed=1).roll_dice()
        assert 1 <= d1 <= 6 and 1 <= d2 <= 6

    def test_the_same_seed_replays_identically(self):
        a = Game(["A", "B"], seed=77)
        b = Game(["A", "B"], seed=77)
        assert [a.roll_dice() for _ in range(10)] == [b.roll_dice() for _ in range(10)]
        assert a.board.to_dict() == b.board.to_dict()

    def test_building_is_refused_without_the_resources(self):
        game = Game(["A", "B"], seed=1)
        assert not game.build(BuildingType.SETTLEMENT, (0, 0))

    def test_building_succeeds_and_charges_the_player(self):
        game = Game(["A", "B"], seed=1)
        player = game.current_player
        for resource, amount in BUILD_COSTS[BuildingType.SETTLEMENT].items():
            player.add_resource(resource, amount)
        assert game.build(BuildingType.SETTLEMENT, (0, 0))
        assert player.total_resources() == 0
        assert (0, 0) in player.settlements

    def test_bank_trade_needs_the_full_ratio(self):
        game = Game(["A", "B"], seed=1)
        player = game.current_player
        player.add_resource(Resource.WOOD, 3)
        assert not game.bank_trade(Resource.WOOD, Resource.ORE, ratio=4)
        player.add_resource(Resource.WOOD, 1)
        assert game.bank_trade(Resource.WOOD, Resource.ORE, ratio=4)
        assert player.resources[Resource.WOOD] == 0
        assert player.resources[Resource.ORE] == 1

    def test_state_is_json_serialisable(self):
        import json

        json.dumps(Game(["A", "B"], seed=1).state())

    def test_the_win_threshold_is_ten(self):
        assert POINTS_TO_WIN == 10
