import functools
from datetime import datetime

import emoji
import pytz
import handleDB
from Utils import escape


class Spettacolo:
    def __init__(self, id_spettacolo, id_film, data_ora, sala, data, ora):
        self.id_spettacolo = id_spettacolo
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
    if a.data_ora.date() < b.data_ora.date():
        return -1
    elif a.data_ora.date() > b.data_ora.date():
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


def get_spettacoli_per_data(logging, data_limite=pytz.timezone("Europe/Rome").localize(datetime(4000, 1, 1, 0, 0))):
    db_conn = handleDB.connect_to_db(logging)
    if db_conn is None:
        print("ERRORE - Impossibile creare connessione con il DB")
        raise Exception("ERRORE - Impossibile creare connessione con il DB")
    spettacoli = handleDB.select_spettacoli(db_conn)
    if not spettacoli:
        return ""
    ordina_spettacoli_giorno_film(spettacoli)
    out = ""
    data_precedente = ""
    id_film_precedente = ""
    for spettacolo in spettacoli:
        if data_precedente != spettacolo.data:
            if pytz.timezone("Europe/Rome").localize(spettacolo.data_ora) > data_limite:
                break
            data_precedente = spettacolo.data
            id_film_precedente = ""
            out += "\n:calendar: Film di " + spettacolo.data + "\n"
        if id_film_precedente != spettacolo.id_film:
            id_film_precedente = spettacolo.id_film
            out += handleDB.select_film(db_conn, spettacolo.id_film).titolo + "\n"
        out += "- " + spettacolo.ora + " sala " + str(spettacolo.sala) + "\n"
    db_conn.close()
    return out


def render_spettacoli(spettacoli):
    message = ""
    if spettacoli:
        for spettacolo in spettacoli:
            data_local = None
            if spettacolo.data_ora != data_local:
                data_local = spettacolo.data_ora
                message += ":calendar:Spettacoli di " + spettacolo.data + "\n"
            message += spettacolo.ora + " - sala " + str(spettacolo.sala) + "\n"
    return emoji.emojize(escape(message), use_aliases=True)
