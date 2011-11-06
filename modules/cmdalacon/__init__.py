#! /usr/bin/env python
#-*- coding: utf-8 -*-
import ConfigParser
import random
import re
from lib.modules import MultiSyncModule, answercmd

def multiwordReplace(text, wordDic):
    """
    take a text and replace words that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, wordDic)))
    def translate(match):
        return wordDic[match.group(0)]
    return rc.sub(translate, text)


class ListConfigParser(ConfigParser.RawConfigParser):   
    def get(self, section, option):
        "Redéfinition du get pour gérer les listes"
        value = ConfigParser.RawConfigParser.get(self, section, option)
        if (value[0] == "[") and (value[-1] == "]"):
            return eval(value)
        else:
            return value

class CmdAlacon(MultiSyncModule):
    def __init__(self, bot):
        commands = self.readconf()
        commands = self.gen_descriptor()
        MultiSyncModule(bot,
                        commands = commands)
    
    def extract_to(self, cmd, value, backup):
        try:
            v = config.get(cmd, value)
        except ConfigParser.NoSectionError:
            v = config.get(cmd, backup)
        if type(v) != list:
            v = [v]
        self.dico[cmd][value] = v

    def readconf(self):
        #name, description and actions associated to each command
        self.dico = {}
        #To initialize MultiSyncModule
        commands = {}

        config = ListConfigParser()
        config.read('modules/cmdalacon/cmdlist.cfg')
        for c in config.sections() :
            self.dico[c] = {}
            commands[c] = self.dico[c]['desc']
            self.dico[c]['desc'] = config.get(c, 'desc') 
            self.dico[c]['toNobody'] = config.get(c, 'toNobody') if type(config.get(c, 'toNobody')) == list else [config.get(c, 'toNobody')]
            self.extract_to(self, c, "toSender", "toNobody")
            self.extract_to(self, c, "toBot", "toSender")
            self.extract_to(self, c, "toSomebody", "toNobody")
        return commands
    
    @answercmd
    def answer(self, cmd, sender, message):
        toall = [self.bot.jid2pseudo(people) for people in self.bot.droits.iterkeys() if self.bot.jid2pseudo(people) not in [self.bot.name, sender]]
        replacement = {"__somebody__":message, "__sender__":sender, "_all_":" ".join(toall)}
        if message.lower() == sender.lower():
            key = "toSender"
        elif message == '':
            key = "toNobody"
        elif message.lower() == self.bot.name.lower():
            key = "toBot"
        else:
            key = "toSomebody"
        return multiwordReplace(multiwordReplace(random.choice(self.dico[cmd][key]), replacement), replacement)
