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

from tests.unit.utils import *
from libmagic import GameMode, FreeForAll, Game, Player, Deck, Card, Land, Cost

def test_create_game_mode():
    game_mode = GameMode()
    assert game_mode

def test_create_game_mode_returns_GameMode():
    game_mode = GameMode()
    assert isinstance(game_mode, GameMode)

def test_initialize_game_mode_keeps_track_of_game():
    game = Game()
    game_mode = GameMode()
    game_mode.initialize(game)
    assert game_mode.game is game

def test_game_mode_validates_decks_for_repeated_cards():
    game_mode = GameMode()
    cards_a = [Card("Some card", Cost.empty())] * 5
    deck_a = Deck("deck a", cards_a)

    is_valid, message = game_mode.validate_deck(deck_a)
    assert not is_valid
    assert message == "There can be only 4 cards of type Card and name Some card in the deck and more than that was found."

def test_game_mode_validate_ignores_repeated_lands():
    game_mode = GameMode()
    cards_a = [Land("Some land", "green")] * 20
    deck_a = Deck("deck a", cards_a)

    is_valid, message = game_mode.validate_deck(deck_a)
    assert is_valid
    assert not message

