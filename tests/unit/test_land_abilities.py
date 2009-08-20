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

from libmagic import Game, Player, Deck, Card, Land, FreeForAll, GameMode, InvalidOperationError, Cost
from libmagic.abilities import *
from tests.unit.utils import *
import tests.unit.data as data

def test_generate_mana_and_tap_ability_raises_when_not_initialized():
    assert_raises(InvalidOperationError, GenerateManaAndTapAbility(None).execute, exc_pattern=r"The player can only generate mana for cards in his battlefield.")

def test_generate_mana_and_tap_ability_raises_when_card_is_not_played():
    new_game = Game()

    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=deepcopy(data.black_land_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert_raises(InvalidOperationError, bernardo.position.hand[0].GenerateManaAndTap, exc_pattern=r"The player can only generate mana for cards in his battlefield.")

def test_generate_mana_and_tap_ability_raises_when_card_is_tapped():
    new_game = Game()

    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=deepcopy(data.black_land_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land = bernardo.position.hand[0]
    bernardo.play(land)

    land.GenerateManaAndTap()

    assert_raises(InvalidOperationError, land.GenerateManaAndTap, exc_pattern=r"The player can't generate mana out of a tapped card.")

def test_generate_mana_and_tap_ability_generates_one_mana():
    new_game = Game()

    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=deepcopy(data.black_land_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land = bernardo.position.hand[0]
    bernardo.play(land)

    land.GenerateManaAndTap()

    assert bernardo.position.mana["green"] == 1

def test_generate_mana_and_tap_ability_taps_card():
    new_game = Game()

    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=deepcopy(data.black_land_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land = bernardo.position.hand[0]
    bernardo.play(land)

    land.GenerateManaAndTap()

    assert land.is_tapped

def test_generate_mana_and_tap_ability_publishes_mana_generated_event():
    new_game = Game()
    messages = []

    def handle_event(game, position, card):
        messages.append("Card %s tapped to generate 1 %s mana" % (card.name, card.color))

    new_game.bus.subscribe('mana_generated', handle_event)

    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=deepcopy(data.black_land_deck))
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land = bernardo.position.hand[0]
    bernardo.play(land)

    land.GenerateManaAndTap()

    assert len(messages) == 1
    assert messages[0] == "Card Forest tapped to generate 1 green mana"

