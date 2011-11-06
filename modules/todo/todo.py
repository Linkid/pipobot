#! /usr/bin/python2
# -*- coding: utf-8 -*-
import time
from model import Todo
from sqlalchemy.orm.exc import NoResultFound

class CmdTodo:
    """ Gestion de TODO-lists """
    def __init__(self, bot):
        desc = """
    todo list : affiche la liste des todolist existantes.
    todo list [name] : affiche la liste des todo de la liste [name]
    todo add [name] [msg] : crée le nouveau todo [msg] dans la liste [name]
    todo remove [n,...] : supprime les todos d'id [n,...]
    todo search [element]: recherche un TODO qui contient [element]
    """
        SyncModule.__init__(self,   
                                bot, 
                                desc = desc,
                                command = "todo")

    @answercmd("list")
    def list(self, args, sender):
        if args == "":
            tmp = self.bot.session.query(Todo).group_by(Todo.name).all()
            if tmp == []:
                return "Pas de todolist…"
            else:
                return "Toutes les TODO-lists: \n%s"%("\n".join([todo.name for todo in tmp]))
        else:
            try:
                ex = ""
                liste, ex = args.split(' ', 1)
            except:
                liste = args
                if liste == "all":
                    tmp = self.bot.session.query(Todo).order_by(Todo.name).all()
                    listname = ""
                    send = "\n"
                    for elt in tmp:
                        if elt.name != listname:
                            send += "%s: \n" % (elt.name)
                            listname = elt.name
                        send += "\t%s \n" % elt
                else:
                    tmp = self.bot.session.query(Todo).filter(Todo.name == liste).all()
                    if tmp == []:
                        send = ""
                    else:
                        send = "%s :\n%s"%(liste, "\n".join(map(str, tmp)))
                if send.strip() == "":
                    return "TODO-list vide"
                return send
            return "usage: !todo list ou !todo list [une_liste]"
    
    @answercmd("add")
    def add(self, args, sender):
        try:
            liste, msg = args.split(' ', 1)
        except ValueError:
            return "usage: !todo add [une_liste] [un_todo]"
        if liste == "all":
            return "On ne peut pas nommer une liste 'all'"
        todo = Todo(liste, msg, sender, time.time()) 
        self.bot.session.add(todo)
        self.bot.session.commit()
        return "TODO ajouté"

    @answercmd("search")
    def search(self, args, sender):
        if len(args) < 1:
            return "usage: !todo search [champ]"
        else:
            found = self.bot.session.query(Todo).filter(Todo.content.like("%" + args + "%"))
            return "\n".join(map(str, found))

    @answercmd("remove", "delete")
    def remove(self, args, sender):
        send = ""
        if len(args) < 1:
            return "usage !todo remove id1,id2,id3,…"
        else:
            arg = args.split(",")
        for i in arg:
            n = int(i)
            deleted = self.bot.session.query(Todo).filter(Todo.id == n).all()
            if deleted == []:
                send += "Pas de todo d'id %s\n"%(n)
            else:
                self.bot.session.delete(deleted[0])
                send += "%s a été supprimé\n"%(deleted[0])
        self.bot.session.commit()
        return send[0:-1]
