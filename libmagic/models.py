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
from libmagic.phases import *
from libmagic.bus import *

class GameEventHandler(object):
    def __init__(self, game):
        self.game = game

    def perform_game_upkeep(self, game, phase, step):
        if step.name != 'upkeep':
            return
        position = self.game.positions[self.game.current_position]
        for card in position.battlefield:
            card.on_upkeep(self.game, position)

    def perform_game_cleanup(self, game, phase, step):
        if step.name != 'cleanup':
            return
        self.game.positions[self.game.current_position].mana = 0

class Game(object):
    class Position(object):
        def __init__(self, index, game, player):
            self.index = index
            self.game = game
            self.player = player
            self.library = copy.deepcopy(player.deck)
            self.library.shuffle()
            self.graveyard = []
            self.hand = self.library.draw(7)
            self.battlefield = []
            self.mana = 0
            self.current_position = None

        @property
        def hit_points(self):
            return self.game.game_mode.get_hit_points_for(self.player.name)

    def __init__(self, game_mode=None, phases=default_phases):
        self.event_handler = GameEventHandler(self)
        if not game_mode:
            game_mode = FreeForAll()

        self.start_date = None
        self.end_date = None
        self.players = []

        game_mode_is_required = 'The game mode must be a GameMode subclass and is required.'
        ct = ConfirmType(subclass=GameMode, messages={'empty':game_mode_is_required, 'noneType':game_mode_is_required, 'subclass':game_mode_is_required})
        ct.to_python(game_mode)

        self.game_mode = game_mode
        self.turn = 0
        self.phases = phases
        self.bus = Bus()

        self.current_phase = None
        self.current_step = None

    def add_player(self, player, supress_validation=False):
        is_valid, message = self.game_mode.validate_deck(player.deck)
        if not is_valid and not supress_validation:
            raise InvalidOperationError(message)
        self.players.append(player)

    def initialize(self):
        if len(self.players) < 2:
            raise RuntimeError("You can't start a game with less than 2 players.")

        self.positions = []
        for player_index, player in enumerate(self.players):
            position = Game.Position(index=player_index, game=self, player=player)
            player.position = position
            player.game = self
            self.positions.append(position)
            for card in position.library.cards:
                card.initialize(self, position)

        self.game_mode.initialize(self)
        self.bus.subscribe('step_started', self.event_handler.perform_game_cleanup)
        self.bus.subscribe('step_started', self.event_handler.perform_game_upkeep)
        self.turn = 1

        self.advance_auto_phases()

    def advance_auto_phases(self):
        for phase in self.phases:
            self.current_phase = phase
            self.bus.publish("phase_started", game=self, phase=phase)
            for step in phase.steps:
                self.current_step = step
                self.bus.publish("step_started", game=self, phase=phase, step=step)
                if not step.automatic:
                    return

    def __move_to_next_position(self):
        if self.current_position >= len(self.positions) - 1:
            self.current_position = 0
            self.turn += 1
        else:
            self.current_position += 1

        self.bus.publish("position_changed", 
                          game=self, 
                          position_index=self.current_position, 
                          position=self.positions[self.current_position])

    def __move_to_next_phase(self):
        if self.phases.index(self.current_phase) >= len(self.phases) - 1:
            self.__move_to_next_position()
            self.current_phase = self.phases[0]
        else:
            self.current_phase = self.phases[self.phases.index(self.current_phase)+1]

        self.bus.publish("phase_started", game=self, phase=self.current_phase)

    def move_to_next_step(self):
        if self.current_phase.steps.index(self.current_step) >= len(self.current_phase.steps) - 1:
            self.__move_to_next_phase()
            self.current_step = self.current_phase.steps[0]
        else:
            self.current_step = self.current_phase.steps[self.current_phase.steps.index(self.current_step) + 1]
    
        self.bus.publish("step_started", game=self, phase=self.current_phase, step=self.current_step)
        if self.current_step.automatic:
            self.move_to_next_step()

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
        self.position = None
        self.game = None

    def play(self, card):
        if not self.game or not self.position:
            raise GameNotInitializedError("You must call game.initialize() before trying to play a card.")

        if self.game.current_position != self.position.index:
            raise InvalidOperationError("It's not %s's turn to play." % self.name)

        if card not in self.position.hand:
            raise InvalidOperationError("The card must be in the player's hand in order to be played.")

        is_valid, message = card.validate_play(self.game, self.position)
        if not is_valid:
            raise InvalidOperationError(message)

        self.position.hand.remove(card)
        self.position.battlefield.append(card)

        card.on_play(self.game, self.position)

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

        self.is_tapped = False
        self.game = None
        self.position = None

    def initialize(self, game, position):
        self.game = game
        self.position = position

    def validate_play(self, game, position):
        pass

    def on_play(self, game, position):
        pass

    def on_upkeep(self, game, position):
        pass

class Land(Card):
    has_played_land = {}
    def __init__(self, name):
        super(Land, self).__init__(name, 0)

    def initialize(self, game, position):
        super(Land, self).initialize(game=game, position=position)
        game.bus.subscribe('step_started', self.handle_upkeep_step)

    def handle_upkeep_step(self, game, phase, step):
        if step.name != "upkeep": 
            return

        Land.has_played_land[game.current_position] = False

    def validate_play(self, game, position):
        super(Land, self).validate_play(game, position)

        has_played = position.index in Land.has_played_land and Land.has_played_land[position.index]

        return (not has_played, "The player can only play one land per turn.")

    def on_upkeep(self, game, position):
        super(Land, self).on_play(game, position)
        self.is_tapped = False

    def on_play(self, game, position):
        super(Land, self).on_play(game, position)
        Land.has_played_land[position.index] = True

    def generate_mana(self):
        if not self.game or not self in self.position.battlefield:
            raise InvalidOperationError(r"The player can only generate mana for terrains in his battlefield.")

        self.position.mana += 1
        self.is_tapped = True
        self.game.bus.publish('mana_generated', self.game, self.position, self)

class GameNotInitializedError(RuntimeError):
    pass

class InvalidOperationError(RuntimeError):
    pass
