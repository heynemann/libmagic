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

from libmagic import Bus

def test_can_create_bus():
    bus = Bus()
    assert bus

def test_created_bus_is_a_Bus():
    bus = Bus()
    assert isinstance(bus, Bus)

def test_bus_can_publish_messages_with_no_listeners():
    bus = Bus()
    bus.publish("some message", text="some")

    assert True, "If it got this far the message was published without errors."

def test_can_subscribe_to_unpublished_message():
    bus = Bus()
    func = lambda x: x
    bus.subscribe("some message", func)

    assert "some message" in bus.subscribers
    assert len(bus.subscribers["some message"]) == 1
    assert bus.subscribers["some message"][0] is func

def test_can_subscribe_and_get_results_on_publish():
    results = []
    def proc(x):
        results.append(x)

    bus = Bus()
    func = proc
    bus.subscribe("some message", func)

    bus.publish("some message", x="text")

    assert len(results) == 1
    assert results[0] == "text"

def test_can_subscribe_and_get_results_on_publish_for_more_than_one_subscriber():
    results = []
    def proc(x):
        results.append(x + "1")
    def proc2(x):
        results.append(x + "2")

    bus = Bus()
    bus.subscribe("some message", proc)
    bus.subscribe("some message", proc2)

    bus.publish("some message", x="text")

    assert len(results) == 2
    assert results[0] == "text1"
    assert results[1] == "text2"

