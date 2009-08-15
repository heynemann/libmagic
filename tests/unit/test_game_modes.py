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

from libmagic import GameMode, Game

def test_create_game_mode():
    game_mode = GameMode()
    assert game_mode

def test_create_game_mode_returns_GameMode():
    game_mode = GameMode()
    assert isinstance(game_mode, GameMode)

def test_initialize_game_mode_keeps_track_of_game():
    game = Game()
    game_mode = GameMode()
    game_mode.initialize(game)
    assert game_mode.game is game

