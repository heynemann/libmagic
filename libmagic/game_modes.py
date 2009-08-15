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

class GameMode(object):
    def initialize(self, game):
        self.game = game
        self.hit_points = {}

    def get_hit_points_for(self, player_name):
        return self.hit_points[player_name]

    def set_hit_points_for(self, player_name, hit_points):
        self.game.game_mode.hit_points[player_name] = hit_points

class FreeForAll(GameMode):
    def __init__(self):
        super(FreeForAll, self).__init__()
        self.hit_points = {}

    def initialize(self, game):
        super(FreeForAll, self).initialize(game)

        for position in game.positions:
            self.set_hit_points_for(position.player.name, 20)

        self.game.current_position = self.decide_first_player()

    def decide_first_player(self):
        index = -1

        while True:
            greatest_cost_card_player_index = 0
            for player_index, position in enumerate(self.game.positions):
                if position.library.cards[index].cost > greatest_cost_card_player_index:
                    greatest_cost_card_player_index = player_index
            if greatest_cost_card_player_index > 0:
                return greatest_cost_card_player_index

            index -= 1
            for player_index, position in enumerate(self.game.positions):
                if abs(index) > len(position.library.cards):
                    return 0

