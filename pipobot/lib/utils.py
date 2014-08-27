#! /usr/bin/python
#-*- coding: utf-8 -*-

import codecs
from ConfigParser import RawConfigParser
import random
import re
import urllib
import httplib
import htmlentitydefs
from xml.etree import cElementTree as ET
from BeautifulSoup import BeautifulSoup, SoupStrainer
from HTMLParser import HTMLParseError

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text.startswith("&#"):
            # character reference
            try:
                if text.startswith("&#x"):
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, text)


def xhtml2text(html):
#fonction de conversion xHTML -> texte pour les clients
#ne supportant pas la XEP-0071
    # on symbolise le gras par "*"
    html = re.sub('<[^>]*b>', '*', html)
    html = re.sub('<[^>]*strong>', '*', html)
    # le souligné par "_"
    html = re.sub('<[^>]*u>', '_', html)
    # On récupère le lien dans les balises <a>
    p = re.compile('<a.*?(?<=href=\")((?:http|www)[^"]*)[^>]*>(.*?)</a>', re.S)
    html = p.sub(r'\2 (\1)', html)
    # on enlève toutes les autres balises
    html = re.sub('<[^>]*>', '', html)

    return unescape(html)


def change_status(user, msg, bot, perm):
    iq = bot.makeIqSet()
    iq["to"] = bot.chatname
    query = ET.Element('{http://jabber.org/protocol/muc#admin}query')
    item = ET.Element('{http://jabber.org/protocol/muc#admin}item', {'nick': user, 'role': perm})
    reason_el = ET.Element('{http://jabber.org/protocol/muc#admin}reason')
    reason_el.text = msg
    item.append(reason_el)
    query.append(item)
    iq.append(query)
    bot.send(iq)


def kick(to_kick, msg, bot):
    change_status(to_kick, msg, bot, 'none')


def mute(to_mute, msg, bot):
    change_status(to_mute, msg, bot, 'visitor')


def unmute(to_unmute, msg, bot):
    change_status(to_unmute, msg, bot, "participant")


class AppURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = ("Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+"
               "(KHTML, like Gecko) Safari/531.2+ Midori/0.2")
urllib._urlopener = AppURLopener()


def check_url(url, geturl=False):
    send = []
    try:
        o = urllib.urlopen(url)
        ctype, clength = o.info().get("Content-Type"), o.info().get("Content-Length")
        if  o.info().gettype() == "text/html":
            title = 'Pas de titre'
            html = o.read(1000000)
            try:
                SoupList = BeautifulSoup(unescape(html),
                                         parseOnlyThese=SoupStrainer('title'))
            except UnicodeDecodeError:
                SoupList = BeautifulSoup(unescape(html.decode("latin1", "ignore")),
                                         parseOnlyThese=SoupStrainer('title'))
            try:
                titles = [title for title in SoupList]
                title = xhtml2text(titles[0].renderContents())
            except IndexError:
                title = "Pas de titre"
            except HTMLParseError:
                pass
            if geturl:
                send.append("%s : [Lien] Titre : %s" %
                            (o.geturl(), " ".join(title.split())))
            else:
                send.append("[Lien] Titre : %s" % " ".join(title.split()))
        else:
            send.append("[Lien] Type: %s, Taille : %s octets" % (ctype, clength))
        o.close()
    except IOError as error:
        if error[1] == 401:
            send.append("Je ne peux pas m'authentifier sur %s :'(" % url)
        elif error[1] == 404:
            send.append("%s n'existe pas !" % url)
        elif error[1] == 403:
            send.append("Il est interdit d'accéder à %s !" % url)
        else:
            send.append("Erreur %s sur %s" % (error[1], url))
    except httplib.InvalidURL:
        send.append("L'URL %s n'est pas valide !" % url)
    return send

#Coloration functions

color_codes = {
    'black':     '0;30',     'bright gray':   '0;37',
    'blue':      '0;34',     'white':         '1;37',
    'green':     '0;32',     'bright blue':   '1;34',
    'cyan':      '0;36',     'bright green':  '1;32',
    'red':       '0;31',     'bright cyan':   '1;36',
    'purple':    '0;35',     'bright red':    '1;31',
    'yellow':    '0;33',     'bright purple': '1;35',
    'dark gray': '1;30',     'bright yellow': '1;33',
    'normal':   '0'
}


def color(txt, color_name):
    return "\033[%sm%s\033[0m" % (color_codes[color_name], txt)


def rdyell(mod, message):
    ret = ""
    for c in message:
        ret += c.upper() if random.randint(0, 1) == 1 else c
    return ret


def rd_censored(mod, message):
    ret = ""
    for c in message:
        if c == " ":
            ret += c
        else:
            ret += "*" if random.randint(0, 5) > 4 else c
    return ret

def rot13(mod, message):
    return codecs.encode(message, "rot13")


class ListConfigParser(RawConfigParser):
    def get(self, section, option):
        "Redéfinition du get pour gérer les listes"
        value = RawConfigParser.get(self, section, option)
        if (value[0] == "[") and (value[-1] == "]"):
            return map(lambda s: s.decode("utf-8"), eval(value))
        else:
            return value.decode("utf-8")
