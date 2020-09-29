import functools
from datetime import datetime

import handleDB


class Spettacolo:
    def __init__(self, xxx_todo_changeme):
        (id, id_film, data_ora, sala, data, ora) = xxx_todo_changeme
        self.id = id
        self.id_film = id_film
        self.data_ora = data_ora
        self.sala = sala
        self.data = data
        self.ora = ora


def ordina_spettacoli_giorno_film(spettacoli):
    if not spettacoli:
        return []
    spettacoli.sort(key=functools.cmp_to_key(compare_spettacoli_giorno_film))


def ordina_spettacoli_film_data(spettacoli):
    if spettacoli is []:
        return []
    spettacoli.sort(key=functools.cmp_to_key(compare_spettacoli_film_data))


def ordina_spettacoli_data(spettacoli):
    if spettacoli is []:
        return []
    spettacoli.sort(key=functools.cmp_to_key(compare_spettacoli_data))


def compare_spettacoli_giorno_film(a, b):
    a_giorno = string2date(a.data_ora)
    b_giorno = string2date(b.data_ora)
    if a_giorno.date() < b_giorno.date():
        return -1
    elif a_giorno.date() < b_giorno.date():
        return 1
    else:
        return compare_spettacoli_film_data(a, b)


def compare_spettacoli_film_data(a, b):
    if a.id_film < b.id_film:
        return -1
    elif a.id_film > b.id_film:
        return 1
    else:
        return compare_spettacoli_data(a, b)


def compare_spettacoli_data(a, b):
    if a.data_ora < b.data_ora:
        return -1
    elif a.data_ora == b.data_ora:
        return 0
    else:
        return 1


def string2date(input):
    return datetime.strptime(input[0:11], "%Y-%m-%dT")


def render_spettacoli_per_data(db_conn, spettacoli):
    if not spettacoli:
        return ""
    ordina_spettacoli_giorno_film(spettacoli)
    out = ""
    data_precedente = ""
    id_film_precedente = ""
    for spettacolo in spettacoli:
        if data_precedente != spettacolo.data:
            data_precedente = spettacolo.data
            out += "\n:calendar: Film di " + spettacolo.data + "\n"
        if id_film_precedente != spettacolo.id_film:
            id_film_precedente = spettacolo.id_film
            out += handleDB.select_film(db_conn, spettacolo.id_film).titolo + "\n"
        out += "- " + spettacolo.ora + " sala " + str(spettacolo.sala) + "\n"
    return out
