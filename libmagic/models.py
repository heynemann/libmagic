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
from libmagic.abilities import *
from libmagic.errors import *

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
        self.game.positions[self.game.current_position].clear_mana()

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
            self.clear_mana()

        def clear_mana(self):
            self.mana = {
                "green":0,
                "red":0,
                "black":0,
                "white":0,
                "blue":0,
                "colorless":0,
            }

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
        self.current_position = None

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
                for ability in card.abilities:
                    ability.initialize(self, position)

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

        if not card.cost.is_satisfied_by(**self.position.mana):
            raise InvalidOperationError("The card cost must be satisfied in order for it to be played.")

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

class Cost(object):
    def __init__(self, **kw):
        self.red = "red" in kw and kw["red"] or 0
        self.black = "black" in kw and kw["black"] or 0
        self.white = "white" in kw and kw["white"] or 0
        self.blue = "blue" in kw and kw["blue"] or 0
        self.green = "green" in kw and kw["green"] or 0
        self.colorless = "colorless" in kw and kw["colorless"] or 0

    @classmethod
    def empty(cls):
        return Cost()

    @property
    def absolute(self):
        return self.red + self.black + self.white + self.blue + self.green + self.colorless

    def is_satisfied_by(self, **kw):
        payable_red = "red" in kw and kw["red"] or 0
        payable_black = "black" in kw and kw["black"] or 0
        payable_white = "white" in kw and kw["white"] or 0
        payable_blue = "blue" in kw and kw["blue"] or 0
        payable_green = "green" in kw and kw["green"] or 0
        payable_colorless = "colorless" in kw and kw["colorless"] or 0

        if payable_red < self.red:
            return False
        if payable_black < self.black:
            return False
        if payable_green < self.green:
            return False
        if payable_white < self.white:
            return False
        if payable_blue < self.blue:
            return False

        mana_available = payable_red - self.red + \
                         payable_green - self.green + \
                         payable_white - self.white + \
                         payable_black - self.black + \
                         payable_blue - self.blue + \
                         payable_colorless

        if mana_available < self.colorless:
            return False

        return True

class Card(object):
    def __init__(self, name, cost):
        name_is_required = 'The card name must be a string and is required.'
        ne = NotEmpty(messages={'empty':name_is_required, 'noneType':name_is_required, 'badType':name_is_required})
        self.name = ne.to_python(name)

        cost_is_required = "The card must have a cost of type Cost (even if it's zero mana)."
        ne = NotEmpty(messages={'empty':cost_is_required, 'noneType':cost_is_required, 'badType':cost_is_required})
        ct = ConfirmType(type=(Cost), messages={'empty':cost_is_required, 'noneType':cost_is_required, 'type':cost_is_required})
        self.cost = ct.to_python(ne.to_python(cost))

        self.is_tapped = False
        self.game = None
        self.position = None
        self.abilities = []

    def initialize(self, game, position):
        self.game = game
        self.position = position
        self.abilities = []

    def validate_play(self, game, position):
        return (True, None)

    def on_play(self, game, position):
        pass

    def on_upkeep(self, game, position):
        pass

    def __getattr__(self, name):
        if name.startswith("__") or name == "abilities":
            return object.__getattribute__(self, name)

        for ability in self.abilities:
            if ability.__class__.__name__.replace("Ability","") == name:
                return ability.execute

        raise AttributeError, name

class Land(Card):
    has_played_land = {}
    def __init__(self, name, color):
        super(Land, self).__init__(name, Cost.empty())
        self.color = color

    def initialize(self, game, position):
        super(Land, self).initialize(game=game, position=position)
        game.bus.subscribe('step_started', self.handle_upkeep_step)
        self.abilities.append(GenerateManaAndTapAbility(self))

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

