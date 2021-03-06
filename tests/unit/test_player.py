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

from tests.unit.utils import *
import tests.unit.data as data
from libmagic import Game, Player, Cost, Deck, Card, Land, GameNotInitializedError, InvalidOperationError

def test_can_create_player():
    new_player = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    assert new_player

def test_created_player_is_Player():
    new_player = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    assert isinstance(new_player, Player)

def test_create_player_raises_on_null_name():
    assert_raises(Invalid, Player.__call__, name=None, deck=deepcopy(data.green_deck), exc_pattern=r'The player name must be a string and is required.')

def test_create_player_raises_on_empty_name():
    assert_raises(Invalid, Player.__call__, name="", deck=deepcopy(data.green_deck), exc_pattern=r'The player name must be a string and is required.')

def test_create_player_keeps_name():
    new_player = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    assert new_player.name == "Bernardo"

def test_create_player_raises_on_null_deck():
    assert_raises(Invalid, Player.__call__, name="Bernardo", deck=None, exc_pattern=r'The deck must be a Deck and is required.')

def test_create_player_raises_on_invalid_type_deck():
    assert_raises(Invalid, Player.__call__, name="Bernardo", deck="deck", exc_pattern=r'The deck must be a Deck and is required.')

def test_create_player_keeps_deck():
    some_deck = deepcopy(data.green_deck)
    new_player = Player(name="Bernardo", deck=some_deck)
    assert new_player.deck is some_deck

def test_player_starts_with_null_position():
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    assert bernardo.position is None

def test_player_starts_with_null_game():
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    assert bernardo.game is None

def test_player_in_a_game_has_game_assigned():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=data.black_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert bernardo.game is new_game
    assert john.game is new_game

def test_player_in_a_game_has_position_assigned():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_deck))
    john = Player(name="John", deck=data.black_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    assert bernardo.position is new_game.positions[0]
    assert john.position is new_game.positions[1]

def test_player_can_play_land():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=data.black_land_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land_to_play = bernardo.position.hand[0]
    bernardo.play(land_to_play)

    assert len(bernardo.position.hand) == 6
    assert len(bernardo.position.battlefield) == 1
    assert bernardo.position.battlefield[0] == land_to_play

def test_playing_a_land_before_initialize_raises():
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    land_to_play = bernardo.deck.cards[0]
    assert_raises(GameNotInitializedError, bernardo.play, card=land_to_play, exc_pattern=r'You must call game.initialize\(\) before trying to play a card.')

def test_playing_a_land_when_not_player_turn_raises():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=data.black_land_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land_to_play = john.position.hand[0]
    assert_raises(InvalidOperationError, john.play, card=land_to_play, exc_pattern=r"It's not John's turn to play.")

def test_playing_a_land_when_not_in_players_hand_raises():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=data.black_land_deck)

    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land_to_play = Land("Some Land", "green")
    assert_raises(InvalidOperationError, bernardo.play, card=land_to_play, exc_pattern=r"The card must be in the player's hand in order to be played.")

def test_playing_two_lands_in_the_same_turn_fails():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=data.black_land_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land_to_play = bernardo.position.hand[0]
    bernardo.play(land_to_play)

    land_to_play = bernardo.position.hand[0]
    assert_raises(InvalidOperationError, bernardo.play, card=land_to_play, exc_pattern=r"The player can only play one land per turn.")

def test_player_can_play_two_lands_in_different_turns():
    new_game = Game()
    bernardo = Player(name="Bernardo", deck=deepcopy(data.green_land_deck))
    john = Player(name="John", deck=data.black_land_deck)
    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    land_to_play = bernardo.position.hand[0]
    bernardo.play(land_to_play)

    new_game.move_to_next_step() #combat - declare_attackers
    new_game.move_to_next_step() #combat - declare_blockers
    new_game.move_to_next_step() #combat - damage
    new_game.move_to_next_step() #main - main
    new_game.move_to_next_step() #main - main (other player)

    new_game.move_to_next_step() #combat - declare_attackers
    new_game.move_to_next_step() #combat - declare_blockers
    new_game.move_to_next_step() #combat - damage
    new_game.move_to_next_step() #main - main
    new_game.move_to_next_step() #main - main (other player)

    land_to_play = bernardo.position.hand[0]
    bernardo.play(land_to_play)

    assert len(bernardo.position.hand) == 5
    assert len(bernardo.position.battlefield) == 2
    assert bernardo.position.battlefield[1] == land_to_play

def test_playing_a_card_without_having_the_cost_raises():
    new_game = Game()
    deck_a = Deck("some_deck", [Card("some card %d" % cnt, Cost(green=4)) for cnt in range(20)])
    deck_b = Deck("some_deck_b", [Card("some card %d " % cnt, Cost(black=3)) for cnt in range(20)])

    bernardo = Player(name="Bernardo", deck=deck_a)
    john = Player(name="John", deck=deck_b)

    new_game.add_player(bernardo)
    new_game.add_player(john)

    new_game.initialize()

    card_to_play = bernardo.position.hand[0]
    assert_raises(InvalidOperationError, bernardo.play, card=card_to_play, exc_pattern=r"The card cost must be satisfied in order for it to be played.")

def test_cost_validates_cost_for_red():
    assert not Cost(red=4).is_satisfied_by(red=2)

def test_cost_validates_cost_for_green():
    assert not Cost(green=4).is_satisfied_by(green=2)

def test_cost_validates_cost_for_white():
    assert not Cost(white=4).is_satisfied_by(white=2)

def test_cost_validates_cost_for_black():
    assert not Cost(black=4).is_satisfied_by(black=2)

def test_cost_validates_cost_for_blue():
    assert not Cost(blue=4).is_satisfied_by(blue=2)

def test_cost_validates_cost_for_colorless():
    assert not Cost(colorless=4).is_satisfied_by(colorless=2)

def test_cost_validates_cost_for_colorless_even_when_many_color_manas_available():
    assert not Cost(colorless=6).is_satisfied_by(red=1, green=1, blue=1, black=1, white=1)

def test_cost_validates_cost_for_colorless_satisfied_by_other_manas():
    assert Cost(colorless=6).is_satisfied_by(red=3, white=2, colorless=1)

