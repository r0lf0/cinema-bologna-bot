import functools
from datetime import datetime

from pytz import timezone

import handleDB


class Spettacolo:
    def __init__(self, xxx_todo_changeme):
        (id_spettacolo, id_film, data_ora, sala, data, ora) = xxx_todo_changeme
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
    a_giorno = string2date(a.data_ora)
    b_giorno = string2date(b.data_ora)
    if a_giorno.date() < b_giorno.date():
        return -1
    elif a_giorno.date() > b_giorno.date():
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


def string2date(input_string):
    return datetime.strptime(input_string[0:11], "%Y-%m-%dT").replace(tzinfo=timezone('Europe/Rome'))


def string2datetime(input_string):
    return datetime.strptime(input_string, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone('Europe/Rome'))


def get_spettacoli_per_data(logging, data_limite=datetime(4000, 1, 1, 0, 0)):
    db_conn = handleDB.create_db(r"cinema.db", logging)
    if db_conn is None:
        print("ERRORE - Impossibile creare connessione con il DB")
        raise Exception("ERRORE - Impossibile creare connessione con il DB")
    handleDB.create_tables(db_conn, logging)
    spettacoli = handleDB.select_spettacoli(db_conn)
    if not spettacoli:
        return ""
    ordina_spettacoli_giorno_film(spettacoli)
    out = ""
    data_precedente = ""
    id_film_precedente = ""
    for spettacolo in spettacoli:
        if data_precedente != spettacolo.data:
            if string2datetime(spettacolo.data_ora) > data_limite:
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
