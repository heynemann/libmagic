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

from libmagic import Game, Player, Deck, Card, Land, FreeForAll, GameMode, InvalidOperationError, Cost
from tests.unit.utils import *
import tests.unit.data as data

def test_create_card():
    card = Card("some card", Cost())
    assert card

def test_create_card_returns_card():
    card = Card("some card", Cost())
    assert isinstance(card, Card)

def test_create_card_keeps_name():
    card = Card("some card", Cost())
    assert card.name == "some card"

def test_create_card_keeps_cost():
    card = Card("some card", Cost(green=10))
    assert card.cost.green == 10

def test_create_card_raises_with_null_cost():
    assert_raises(Invalid, Card, name="some_card", cost=None, exc_pattern=r"The card must have a cost of type Cost \(even if it's zero mana\).")

def test_create_card_raises_with_string_cost():
    assert_raises(Invalid, Card, name="some_card", cost="a", exc_pattern=r"The card must have a cost of type Cost \(even if it's zero mana\).")

def test_create_card_raises_with_empty_cost():
    assert_raises(Invalid, Card, name="some_card", cost="", exc_pattern=r"The card must have a cost of type Cost \(even if it's zero mana\).")

def test_create_card_raises_with_null_name():
    assert_raises(Invalid, Card, name=None, cost=10, exc_pattern=r"The card name must be a string and is required.")

def test_create_card_raises_with_empty_name():
    assert_raises(Invalid, Card, name="", cost=10, exc_pattern=r"The card name must be a string and is required.")

def test_create_land_starts_card_with_zero_cost():
    land = Land("some land", color="green")
    assert land.cost.green == 0
    assert land.cost.red == 0
    assert land.cost.blue == 0
    assert land.cost.black == 0
    assert land.cost.white == 0
    assert land.cost.colorless == 0

def test_create_land_keeps_name():
    land = Land("some land", color="green")
    assert land.name == "some land"

def test_card_on_play_works():
    card = Card("some card", Cost())
    card.on_play(None, None)
    assert True, "It shouldn't do anything"

def test_card_on_upkeep_works():
    card = Card("some card", Cost())
    card.on_upkeep(None, None)
    assert True, "It shouldn't do anything"

def test_card_validate_play_works():
    card = Card("some card", Cost())
    card.validate_play(None, None)
    assert True, "It shouldn't do anything"

def test_tapping_lands_not_in_game_raises():
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    land_to_play = bernardo.deck.cards[0]
    assert_raises(InvalidOperationError, land_to_play.generate_mana, exc_pattern=r"The player can only generate mana for terrains in his battlefield.")

def test_tapping_lands_from_hand_raises():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=data.black_land_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land_to_play = bernardo.position.hand[0]

    assert_raises(InvalidOperationError, land_to_play.generate_mana, exc_pattern=r"The player can only generate mana for terrains in his battlefield.")

def test_player_can_tap_lands_to_get_mana():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=data.black_land_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land_to_play = bernardo.position.hand[0]
    bernardo.play(land_to_play)

    land_to_play.generate_mana() #tap to generate mana

    assert bernardo.position.mana["green"] == 1
    assert bernardo.position.mana["black"] == 0
    assert bernardo.position.mana["blue"] == 0
    assert bernardo.position.mana["red"] == 0
    assert bernardo.position.mana["white"] == 0
    assert bernardo.position.mana["colorless"] == 0

    assert land_to_play.is_tapped

def test_generating_mana_out_of_a_tapped_land_raises():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=data.black_land_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land_to_play = bernardo.position.hand[0]
    bernardo.play(land_to_play)

    land_to_play.generate_mana() #tap to generate mana

    assert_raises(InvalidOperationError, land_to_play.generate_mana, exc_pattern=r"The player can't generate mana out of a tapped land.")

