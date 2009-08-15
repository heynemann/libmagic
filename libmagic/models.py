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

from formencode.validators import NotEmpty, ConfirmType

class Game(object):
    class Position(object):
        def __init__(self, player):
            self.player = player
            self.library = copy.deepcopy(player.deck)
            self.library.shuffle()
            self.graveyard = []
            self.hand = self.library.draw(7)
            self.table = []

    def __init__(self):
        self.start_date = None
        self.end_date = None
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def initialize(self):
        if len(self.players) < 2:
            raise RuntimeError("You can't start a game with less than 2 players.")

        self.positions = []
        for player in self.players:
            self.positions.append(Game.Position(player=player))

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
        ne.to_python(name)

        self.name = name
        self.cards = cards

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, number_of_cards):
        cards = self.cards[:number_of_cards]
        del self.cards[:number_of_cards]

        return cards

class Card(object):
    def __init__(self, name):
        self.name = name

class Land(Card):
    pass
