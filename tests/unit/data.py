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

from libmagic import *

forest = Land(name="Forest", color="green")
forest_pack = [forest] * 20
swamp = Land(name="Swamp", color="black")
swamp_pack = [swamp] * 20

green_deck = Deck(name="Green Deck", cards=forest_pack)
black_deck = Deck(name="Black Deck", cards=swamp_pack)

green_land_deck = Deck(name="Green Land Deck", cards=forest_pack)
black_land_deck = Deck(name="Black Land Deck", cards=swamp_pack)
