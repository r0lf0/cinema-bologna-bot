from Film import Film
from Spettacolo import Spettacolo
import sqlite3
from sqlite3 import Error
from datetime import datetime

sql_crea_tabella_film = """ CREATE TABLE IF NOT EXISTS film (
                                id integer,
                                titolo varchar,
                                data_uscita timestamp,
                                regista varchar,
                                attori varchar,
                                trama varchar,
                                durata varchar,
                                trailer_link varchar,
                                locandina blob
                            ); """

sql_crea_tabella_genere = """ CREATE TABLE IF NOT EXISTS genere (
                                    id_film integer,
                                    genere varchar
                                ); """

sql_crea_tabella_spettacolo = """ CREATE TABLE IF NOT EXISTS spettacolo (
                                    id integer,
                                    id_film integer,
                                    data_ora datetime,
                                    sala integer,
                                    data varchar,
                                    ora varchar,
                                    consolidato boolean
                                ); """


def string2datetime(input):
    return datetime.strptime(input, "%Y-%m-%dT%H:%M:%S")


def create_db(db_file, logging):
    db_conn = None
    try:
        db_conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
        logging.error(e)
    return db_conn


def create_table(db_conn, create_table_sql, logging):
    try:
        c = db_conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
        logging.error(e)


def create_tables(db_conn, logging):
    create_table(db_conn, sql_crea_tabella_film, logging)
    create_table(db_conn, sql_crea_tabella_genere, logging)
    create_table(db_conn, sql_crea_tabella_spettacolo, logging)


sql_select_film = """   SELECT *
                        FROM film
                        WHERE id = ? """


def select_film(db_conn, idFilm):
    cur = db_conn.cursor()
    cur.execute(sql_select_film, (idFilm,))
    film_tupla = cur.fetchone()
    if film_tupla is None:
        return None
    return Film(film_tupla)


sql_insert_film = """   INSERT INTO film (id, titolo, data_uscita, regista, attori, trama, durata, trailer_link, locandina)
                        VALUES (?,?,?,?,?,?,?,?,?) """


def insert_film(db_conn, film, generi):
    selected_film = select_film(db_conn, film.id)
    if selected_film is not None:
        return False
    cur = db_conn.cursor()
    cur.execute(sql_insert_film, (
        film.id, film.titolo, film.data_uscita, film.regista, film.attori, film.trama, film.durata, film.trailer_link,
        film.locandina))
    db_conn.commit()
    for genere in generi:
        insert_genere(db_conn, genere)
    return True


sql_insert_genere = """     INSERT INTO genere (id_film, genere)
                            VALUES (?,?) """


def insert_genere(db_conn, genere):
    cur = db_conn.cursor()
    cur.execute(sql_insert_genere, (genere.id_film, genere.genere))
    db_conn.commit()
    return True


sql_select_spettacolo = """ SELECT id, id_film, data_ora, sala, data, ora
                            FROM spettacolo
                            WHERE id = ? """


def select_spettacolo(db_conn, id):
    cur = db_conn.cursor()
    cur.execute(sql_select_spettacolo, (id,))
    spettacolo_tupla = cur.fetchone()
    if spettacolo_tupla is None:
        return None
    return Spettacolo(spettacolo_tupla)


sql_insert_spettacolo = """ INSERT INTO spettacolo (id, id_film, data_ora, sala, data, ora, consolidato)
                            VALUES (?,?,?,?,?,?,1) """

sql_consolida_spettacolo = """  UPDATE spettacolo
                                SET consolidato = 1 
                                WHERE id = ? """


def insert_spettacolo(db_conn, spettacolo):
    selected_spettacolo = select_spettacolo(db_conn, spettacolo.id)
    cur = db_conn.cursor()
    if selected_spettacolo is not None:
        cur.execute(sql_consolida_spettacolo, (spettacolo.id,))
        db_conn.commit()
        return False
    cur.execute(sql_insert_spettacolo, (spettacolo.id, spettacolo.id_film, spettacolo.data_ora, spettacolo.sala,
                                        spettacolo.data, spettacolo.ora))
    db_conn.commit()
    return True


sql_select_spettacoli = """ SELECT id, id_film, data_ora, sala, data, ora
                            FROM spettacolo """

def select_spettacoli(db_conn):
    cur = db_conn.cursor()
    cur.execute(sql_select_spettacoli)
    spettacoli_tupla = cur.fetchall()
    if spettacoli_tupla is None:
        return []
    spettacoli = []
    for spettacolo_tupla in spettacoli_tupla:
        spettacoli.append(Spettacolo(spettacolo_tupla))
    return spettacoli


sql_delete_spettacolo = """ DELETE FROM spettacolo 
                            WHERE id = ?"""


def elimina_spettacoli_passati(db_conn):
    adesso = datetime.now()
    cur = db_conn.cursor()
    cur.execute(sql_select_spettacoli)
    spettacoli = cur.fetchall()
    if spettacoli is None:
        return []

    spettacoli_rimossi = []
    for spettacolo_tupla in spettacoli:
        spettacolo = Spettacolo(spettacolo_tupla)
        if string2datetime(spettacolo.data_ora) < adesso:
            spettacoli_rimossi.append(spettacolo)
            cur.execute(sql_delete_spettacolo, (spettacolo.id,))
    db_conn.commit()
    return spettacoli_rimossi


sql_delete_spettacoli_non_consolidati = """ DELETE FROM spettacolo 
                                            WHERE consolidato = 0 """


def elimina_spettacoli_non_consolidati(db_conn):
    cur = db_conn.cursor()
    cur.execute(sql_delete_spettacoli_non_consolidati)
    db_conn.commit()


sql_select_spettacoli_non_consolidati = """ SELECT id, id_film, data_ora, sala, data, ora
                                            FROM spettacolo 
                                            WHERE consolidato = 0 """


def select_spettacoli_non_consolidati(db_conn):
    cur = db_conn.cursor()
    cur.execute(sql_select_spettacoli_non_consolidati)
    spettacoli_tupla = cur.fetchall()
    if spettacoli_tupla is None:
        return []
    spettacoli = []
    for spettacolo_tupla in spettacoli_tupla:
        spettacoli.append(Spettacolo(spettacolo_tupla))
    return spettacoli


sql_azzera_flag_spettacoli_consolidati = """ UPDATE spettacolo
                                             SET consolidato = 0 """


def azzera_flag_spettacoli_consolidati(db_conn):
    cur = db_conn.cursor()
    cur.execute(sql_azzera_flag_spettacoli_consolidati)
    db_conn.commit()

