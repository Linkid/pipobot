#! /usr/bin/env python
#-*- coding: utf-8 -*-

import lib.utils
from lib.abstract_modules import FortuneModule

class CmdChuck(FortuneModule):
    def __init__(self, bot):
        desc = """Pour afficher des chucknorrisfact.
chuck : Retourne un fact aléatoire.
chuck [n] : Affiche le fact [n]"""
        FortuneModule.__init__(self,
                            bot,  
                            desc = desc,
                            command = "chuck",
                            url_random = "http://www.chucknorrisfacts.fr/index.php?p=parcourir&tri=aleatoire",
                            url_indexed = "http://www.chucknorrisfacts.fr/index.php?p=detail_fact&fact=%s",
                            lock_time = 2,
                            )

    def extract_data(self, soup):
        fact = soup.findAll("div", {"class": "fact"})[0]
        index = fact.get("id").partition("fact")[2]
        content = lib.utils.xhtml2text(fact.text)
        return "Fact #%s : %s"%(index, content)
