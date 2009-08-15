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
from formencode.api import Invalid

from tests.unit.utils import *
from tests.unit.data import *
from libmagic import Deck

def test_create_deck():
    deck = Deck(name="Some Deck", cards=[])
    assert deck

def test_created_deck_is_Deck():
    deck = Deck(name="Some Deck", cards=[])
    assert isinstance(deck, Deck)

def test_create_deck_raises_on_null_name():
    assert_raises(Invalid, Deck.__call__, name=None, cards=[], exc_pattern=r'The deck name must be a string and is required.')

def test_create_deck_raises_on_empty_name():
    assert_raises(Invalid, Deck.__call__, name='', cards=[], exc_pattern=r'The deck name must be a string and is required.')

def test_create_deck_keeps_name():
    new_deck = Deck(name="Bernardo", cards=[])
    assert new_deck.name == "Bernardo"

def test_deck_shuffle():
    new_deck = copy.deepcopy(green_deck)
    new_deck.shuffle()

    assert (new_deck.cards[0] is not green_deck.cards[0]) or (new_deck.cards[-1] is not green_deck.cards[-1])

def test_deck_draw_removes_cards_from_deck():
    new_deck = copy.deepcopy(green_deck)
    new_deck.draw(2)

    assert len(new_deck.cards) == len(green_deck.cards) - 2

def test_deck_draw_removes_first_cards_from_deck():
    new_deck = copy.deepcopy(green_deck)
    first_cards = new_deck.cards[0:2]
    cards = new_deck.draw(2)

    assert cards[0] == first_cards[0]
    assert cards[1] == first_cards[1]

