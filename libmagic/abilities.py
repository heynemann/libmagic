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

from libmagic.errors import *

class Ability(object):
    def __init__(self, card):
        self.card = card
        self.game = None
        self.position = None

    def initialize(self, game, position):
        self.game = game
        self.position = position

class GenerateManaAndTapAbility(Ability):

    def execute(self):
        if not self.game or not self.card in self.position.battlefield:
            raise InvalidOperationError(r"The player can only generate mana for cards in his battlefield.")
        if self.card.is_tapped:
            raise InvalidOperationError(r"The player can't generate mana out of a tapped card.")

        self.position.mana[self.card.color] += 1
        self.card.is_tapped = True
        self.game.bus.publish('mana_generated', self.game, self.position, self.card)
