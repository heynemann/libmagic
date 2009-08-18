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

class Phase(object):
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps

class Step(object):
    def __init__(self, name, automatic=False):
        self.name = name
        self.automatic = automatic

default_phases = [
                    Phase("beggining",
                            [
                                Step("untap", automatic=True),
                                Step("upkeep", automatic=True),
                                Step("draw", automatic=True)
                            ]),
                    Phase("main", [Step("main")]),
                    Phase("combat",
                            [
                                Step("beggining", automatic=True),
                                Step("declare_attackers"),
                                Step("declare_blockers"),
                                Step("damage"),
                                Step("end", automatic=True),
                            ]),
                    Phase("main", [Step("main")]),
                    Phase("ending",
                            [
                                Step("end", automatic=True),
                                Step("cleanup", automatic=True)
                            ])
                 ]
