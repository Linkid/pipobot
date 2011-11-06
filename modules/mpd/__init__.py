#! /usr/bin/python2
# -*- coding: utf-8 -*-

import threading
from lib.BotMPD import BotMPD
from mpd import CommandError
import lib.modules.SyncModule

try:
    import config
except ImportError:
    raise NameError("MPD config not found, unable to start MPD module")
    
class CmdMpd(lib.modules.SyncModule):
    def __init__(self, bot):
        desc = """Controle du mpd
    mpd current : chanson actuelle
    mpd next/prev/play: c'est assez explicite
    mpd shuffle : fait un shuffle sur la playlist
    mpd list [n] : liste les [n] chansons suivantes
    mpd clear : vide la playlist (ou pas)
    mpd search (Artist|Title) requete : cherche toutes les pistes d'Artiste/Titre correspondant à la requête
    mpd setnext [i] : place la chanson à la position [i] dans la playlist après la chanson courante (enfin elle court pas vraiment)
    mpd nightmare [i] : les [i] prochaines chansons vont vous faire souffrir (plus que le reste)
    mpd clean : pour retarder l'inévitable...
    mpd connected : pour consulter le nombre de personnes connectées sur icecast
    mpd settag [artist|title]=Nouvelle valeur"""
        lib.modules.SyncModule.__init(bot, 
                                    desc = desc,
                                    pm_allowed = False,
                                    command = "mpd")
        self.verbose = False

    #TODO passer les commandes de lib/ ici et utiliser les décorateurs
    @answercmd()
    def answer(self, sender, message):
        if hasattr(config, "DATADIR"):
            mpd = BotMPD(config.HOST, config.PORT, config.PASSWORD, config.DATADIR)
        else:
            mpd = BotMPD(config.HOST, config.PORT, config.PASSWORD)
        try:
            cmd, arg = message.split(' ', 1)
        except:
            cmd = message
            arg = ''

        # Table de correspondance entrée <-> méthode de BotMPD
        cmds = {'current': 'current',
                'next': 'next',
                'search': 'search',
                'prev': 'previous',
                'play': 'play',
#                'stop': 'stop',
#                'pause': 'pause',
                'list': 'nextplaylist',
                'settag': 'settag',
                'shuffle': 'shuffle',
                'setnext': 'setnext',
                'nightmare': 'nightmare',
                'clean': 'clean',
                'goto': 'goto',
                'coffee': 'coffee',
                'wakeup': 'wakeup',
                'connected': 'connected',
               }
        if cmd == "mute":
            if self.verbose:
                self.verbose = False
                send = "Bon d'accord je me la ferme mais venez pas bouder après !"
            else:
                send = "... Heu... c'est déjà le cas crétin..."
        elif cmd == "unmute":
            if self.verbose:
                send = "T'es aveugle ou quoi ? Je parle déjà !"
            else:
                self.verbose = True
                send = "C'est vrai je peux ? Vous allez SOUFFRIR !"
        elif cmds.has_key(cmd):
            try:
                if arg == '':
                    send = getattr(mpd, cmds[cmd])()
                else:
                    send = getattr(mpd, cmds[cmd])(arg)
            except (TypeError, CommandError):
                send = getattr(mpd, cmds[cmd])()
        else:
            send = "N'existe pas ça, RTFM. Ou alors tu sais pas écrire ..."

        mpd.disconnect()
        return send
