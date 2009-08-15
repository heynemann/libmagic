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

from tests.unit.utils import *
import tests.unit.data as data
from libmagic import Game, Player, Deck

def test_can_create_game():
    new_game = Game()
    assert new_game

def test_created_game_is_Game():
    new_game = Game()
    assert isinstance(new_game, Game)

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

def test_initialize_created_positions_get_empty_tables():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=deepcopy(data.black_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert not new_game.positions[0].table
    assert not new_game.positions[1].table

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

