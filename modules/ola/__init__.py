#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import time
from lib.modules import SyncModule, answercmd

class Ola(lib.modueles.SyncModule):
    def __init__(self, bot):
        desc = "Fait la ola."
        SyncModule.__init__(bot,
                                desc = desc,
                                command = "ola")

    @answercmd
    def answer(self, sender, message):
        if message == "":
            message = str(random.randint(0, 1))
        if not message.isdigit():
            return "On veut un entier quand même..."
        res = ["\o/ .o. .o. .o.",".o. \o/ .o. .o.",".o. .o. \o/ .o.",".o. .o. .o. \o/"]
        if int(message) % 2 != 0:
            res.reverse()
        return res
