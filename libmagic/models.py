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

import copy
import random

from formencode.validators import NotEmpty, ConfirmType, Int, Set
from libmagic.game_modes import GameMode, FreeForAll

class Game(object):
    class Position(object):
        def __init__(self, game, player):
            self.game = game
            self.player = player
            self.library = copy.deepcopy(player.deck)
            self.library.shuffle()
            self.graveyard = []
            self.hand = self.library.draw(7)
            self.table = []
            self.mana = 0

        @property
        def hit_points(self):
            return self.game.game_mode.get_hit_points_for(self.player.name)

    def __init__(self, game_mode=None):
        if not game_mode:
            game_mode = FreeForAll()

        self.start_date = None
        self.end_date = None
        self.players = []

        game_mode_is_required = 'The game mode must be a GameMode subclass and is required.'
        ct = ConfirmType(subclass=GameMode, messages={'empty':game_mode_is_required, 'noneType':game_mode_is_required, 'subclass':game_mode_is_required})
        ct.to_python(game_mode)

        self.game_mode = game_mode

    def add_player(self, player):
        self.players.append(player)

    def initialize(self):
        if len(self.players) < 2:
            raise RuntimeError("You can't start a game with less than 2 players.")

        self.positions = []
        for player in self.players:
            self.positions.append(Game.Position(game=self, player=player))

        self.game_mode.initialize(self)

class Player(object):
    def __init__(self, name, deck):
        player_is_required = 'The player name must be a string and is required.'
        ne = NotEmpty(messages={'empty':player_is_required, 'noneType':player_is_required, 'badType':player_is_required})
        ne.to_python(name)

        deck_is_required = 'The deck must be a Deck and is required.'
        ct = ConfirmType(type=Deck, messages={'empty':deck_is_required, 'noneType':deck_is_required, 'type':deck_is_required})
        ct.to_python(deck)

        self.name = name
        self.deck = deck

class Deck(object):
    def __init__(self, name, cards):
        deck_is_required = 'The deck name must be a string and is required.'
        ne = NotEmpty(messages={'empty':deck_is_required, 'noneType':deck_is_required, 'badType':deck_is_required})
        self.name = ne.to_python(name)

        cards_are_required = 'The cards property must be a list and is required.'
        ct = ConfirmType(type=(list, tuple), messages={'empty':cards_are_required, 'noneType':cards_are_required, 'inType':cards_are_required})
        self.cards = ct.to_python(cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, number_of_cards):
        cards = self.cards[:number_of_cards]
        del self.cards[:number_of_cards]

        return cards

class Card(object):
    def __init__(self, name, cost):
        name_is_required = 'The card name must be a string and is required.'
        ne = NotEmpty(messages={'empty':name_is_required, 'noneType':name_is_required, 'badType':name_is_required})
        self.name = ne.to_python(name)

        cost_is_required = "The card must have an integer cost (even if it's zero)."
        ne = NotEmpty(messages={'empty':cost_is_required, 'noneType':cost_is_required, 'badType':cost_is_required})
        ct = Int(messages={'empty':cost_is_required, 'noneType':cost_is_required, 'integer':cost_is_required})
        self.cost = ct.to_python(ne.to_python(cost))

class Land(Card):
    def __init__(self, name):
        super(Land, self).__init__(name, 0)

