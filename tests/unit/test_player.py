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
from libmagic import Player, Deck

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

