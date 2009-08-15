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

from formencode.api import Invalid

from tests.unit.utils import *
from libmagic import Card, Land

def test_create_card():
    card = Card("some card", 0)
    assert card

def test_create_card_returns_card():
    card = Card("some card", 0)
    assert isinstance(card, Card)

def test_create_card_keeps_name():
    card = Card("some card", 0)
    assert card.name == "some card"

def test_create_card_keeps_cost():
    card = Card("some card", 10)
    assert card.cost == 10

def test_create_card_raises_with_null_cost():
    assert_raises(Invalid, Card.__call__, name="some_card", cost=None, exc_pattern=r"The card must have an integer cost \(even if it's zero\).")

def test_create_card_raises_with_string_cost():
    assert_raises(Invalid, Card.__call__, name="some_card", cost="a", exc_pattern=r"The card must have an integer cost \(even if it's zero\).")

def test_create_card_raises_with_empty_cost():
    assert_raises(Invalid, Card.__call__, name="some_card", cost="", exc_pattern=r"The card must have an integer cost \(even if it's zero\).")

def test_create_card_raises_with_null_name():
    assert_raises(Invalid, Card.__call__, name=None, cost=10, exc_pattern=r"The card name must be a string and is required.")

def test_create_card_raises_with_empty_name():
    assert_raises(Invalid, Card.__call__, name="", cost=10, exc_pattern=r"The card name must be a string and is required.")

def test_create_land_starts_card_with_zero_cost():
    land = Land("some land")
    assert land.cost == 0

def test_create_land_keeps_name():
    land = Land("some land")
    assert land.name == "some land"
