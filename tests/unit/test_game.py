#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright Bernardo Heynemann <heynemann@gmail.com>

# Licensed under the Open Software License ("OSL") v. 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.opensource.org/licenses/osl-3.0.php

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from copy import deepcopy

from formencode.api import Invalid

from libmagic import Game, Player, Deck, Card, Land, FreeForAll, GameMode
from tests.unit.utils import *
import tests.unit.data as data

def test_can_create_game():
    new_game = Game()
    assert new_game

def test_created_game_is_Game():
    new_game = Game()
    assert isinstance(new_game, Game)

def test_create_game_assigns_free_for_all_as_default_game_mode():
    new_game = Game()
    assert isinstance(new_game.game_mode, FreeForAll)

def test_create_game_assigns_free_for_all_when_null_game_mode():
    new_game = Game(game_mode=None)
    assert isinstance(new_game.game_mode, FreeForAll)

def test_create_game_raises_when_string_game_mode():
    assert_raises(Invalid, Game.__call__, game_mode="wrong", exc_pattern=r"The game mode must be a GameMode subclass and is required.")

def test_create_game_raises_when_int_game_mode():
    assert_raises(Invalid, Game.__call__, game_mode=10, exc_pattern=r"The game mode must be a GameMode subclass and is required.")

def test_create_game_assigns_20_hit_points_for_each_player_on_free_for_all():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=deepcopy(data.black_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert new_game.positions[0].hit_points == 20
    assert new_game.positions[1].hit_points == 20

def test_created_game_has_not_started():
    new_game = Game()
    assert not new_game.start_date

def test_created_game_has_not_finished():
    new_game = Game()
    assert not new_game.end_date

def test_created_game_has_no_players():
    new_game = Game()
    assert not new_game.players

def test_can_add_player():
    new_game = Game()
    new_game.add_player(Player(name="Bernardo", deck=deepcopy(data.green_deck)))
    assert new_game.players

def test_added_player_stays():
    new_game = Game()
    new_game.add_player(Player(name="Bernardo", deck=deepcopy(data.green_deck)))
    assert new_game.players[0].name == "Bernardo"

def test_initialize_raises_runtime_error_if_less_than_two_players():
    new_game = Game()
    new_game.add_player(Player(name="Bernardo", deck=deepcopy(data.green_deck)))

    assert_raises(RuntimeError, new_game.initialize, exc_pattern=r"You can't start a game with less than 2 players.")

def test_initialize_creates_positions():
    new_game = Game()
    new_game.add_player(Player(name="Bernardo", deck=deepcopy(data.green_deck)))
    new_game.add_player(Player(name="John", deck=deepcopy(data.black_deck)))

    new_game.initialize()

    assert new_game.positions

def test_initialize_creates_positions_according_to_the_players():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=deepcopy(data.black_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert len(new_game.positions) == 2
    assert new_game.positions[0].player is bernardo
    assert new_game.positions[1].player is john

def test_initialize_creates_positions_with_right_indexes():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=deepcopy(data.black_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert new_game.positions[0].index == 0
    assert new_game.positions[1].index == 1

def test_initialize_created_positions_get_deep_copies_of_decks():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=deepcopy(data.black_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert new_game.positions[0].library is not bernardo.deck
    assert new_game.positions[1].library is not john.deck

def test_initialize_created_positions_get_empty_graveyards():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=data.black_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert not new_game.positions[0].graveyard
    assert not new_game.positions[1].graveyard

def test_initialize_created_positions_get_empty_battlefields():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=deepcopy(data.black_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert not new_game.positions[0].battlefield
    assert not new_game.positions[1].battlefield

def test_initialize_draws_players_first_hand():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=deepcopy(data.black_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert len(new_game.positions[0].hand) == 7
    assert len(new_game.positions[1].hand) == 7

def test_initialize_makes_libraries_equal_to_deck_minus_hand():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=deepcopy(data.black_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert len(new_game.positions[0].library.cards) == len(bernardo.deck.cards) - 7
    assert len(new_game.positions[1].library.cards) == len(john.deck.cards) - 7

def test_initialize_shuffles_decks_to_libraries():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=deepcopy(data.black_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert new_game.positions[0].library.cards[0] is not bernardo.deck.cards[0]
    assert new_game.positions[1].library.cards[0] is not john.deck.cards[0]

def test_initialize_created_positions_get_zero_mana():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=data.black_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert new_game.positions[0].mana == 0
    assert new_game.positions[1].mana == 0

def test_game_decides_player_to_start():
    new_game = Game()
    cards_a = [Card("Some card", 1)] * 20
    deck_a = Deck("deck a", cards_a)
    bernardo = Player(name="Bernardo", deck=deck_a)
    cards_b = [Card("Some card", 4)] * 20
    deck_b = Deck("deck a", cards_b)
    john = Player(name="John", deck=deck_b)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert new_game.current_position == 1

def test_game_is_at_turn_zero_before_initialized():
    new_game = Game()
    assert new_game.turn == 0

def test_game_is_at_turn_one_after_initialized():
    new_game = Game()
    cards_a = [Card("Some card", 1)] * 20
    deck_a = Deck("deck a", cards_a)
    bernardo = Player(name="Bernardo", deck=deck_a)
    cards_b = [Card("Some card", 4)] * 20
    deck_b = Deck("deck a", cards_b)
    john = Player(name="John", deck=deck_b)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert new_game.turn == 1

