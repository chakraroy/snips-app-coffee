#!/usr/bin/env python2
# -*-: coding utf-8 -*-

import ConfigParser
from coffeehack.coffeehack import CoffeeHack
from hermes_python.hermes import Hermes
import io
import Queue

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name : option for option_name, option in self.items(section)} for section in self.sections()}

def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

class Skill:

    def __init__(self):
        config = read_configuration_file("config.ini")
        extra = config["global"].get("extra", False)
        self.coffee = CoffeeHack(extra = extra)

def extract_value(val):
    res = []
    if val is not None:
        for r in val:
            res.append(r.slot_value.value.value)
    return res

def extract_coffee_taste(intent_message):
    return extract_value(intent_message.slots.coffee_taste)

def extract_coffee_number(intent_message):
    return extract_value(intent_message.slots.coffee_number)

def extract_coffee_type(intent_message):
    return extract_value(intent_message.slots.coffee_type)

def extract_coffee_size(intent_message):
    return extract_value(intent_message.slots.coffee_size)

def callback(hermes, intent_message):
    t = extract_coffee_type(intent_message)
    s = extract_coffee_size(intent_message)
    ta = extract_coffee_taste(intent_message)
    n = extract_coffee_number(intent_message)
    coffee_type = t[0] if len(t) else ""
    coffee_size = s[0] if len(s) else ""
    coffee_taste = ta[0] if len(ta) else ""
    number = 1
    if len(n):
        try:
            number = int(n[0])
        except ValueError, e:
            number = 2
    print(t)
    print(s)
    print(ta)
    hermes.skill.coffee.pour(coffee_type = coffee_type,
                coffee_size = coffee_size,
                coffee_taste = coffee_taste,
                number = number)

def coffee_toggle(hermes, intent_message):
      hermes.skill.coffee.toggle_on_off()
def coffee_clean(hermes, intent_message):
      hermes.skill.coffee.clean()
def coffee_steam(hermes, intent_message):
      hermes.skill.coffee.steam()

if __name__ == "__main__":
    skill = Skill()
    with Hermes(MQTT_ADDR) as h:
        h.skill = skill
        h.subscribe_intent("pour", callback) \
                .subscribe_intent("coffee_toggle", coffee_toggle) \
                .subscribe_intent("clean", coffee_clean) \
                .subscribe_intent("steam", coffee_steam) \
         .loop_forever()
