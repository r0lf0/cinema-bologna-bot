import os

from pytz import timezone

from Film import Film
from Spettacolo import Spettacolo
from datetime import datetime
import psycopg2

from utils.Utils import string2datetime

sql_crea_tabella_film = """ CREATE TABLE IF NOT EXISTS film (
                                id integer NOT NULL,
                                titolo varchar,
                                data_uscita timestamp,
                                regista varchar,
                                attori varchar,
                                trama varchar,
                                durata varchar,
                                trailer_link varchar,
                                locandina_link varchar,
                                locandina bytea,
                                PRIMARY KEY (id)
                            ); """

sql_crea_tabella_genere = """ CREATE TABLE IF NOT EXISTS genere (
                                    id_film integer NOT NULL,
                                    genere varchar NOT NULL,
                                    FOREIGN KEY (id_film) REFERENCES film(id)
                                ); """

sql_crea_tabella_spettacolo = """ CREATE TABLE IF NOT EXISTS spettacolo (
                                    id integer NOT NULL,
                                    id_film integer NOT NULL,
                                    data_ora timestamp NOT NULL,
                                    sala integer,
                                    data varchar,
                                    ora varchar,
                                    consolidato boolean,
                                    PRIMARY KEY (id),
                                    FOREIGN KEY (id_film) REFERENCES film(id)
                                ); """


def connect_to_db(logging):
    db_conn = None
    try:
        db_conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        logging.error(error)
    return db_conn


def create_table(db_conn, create_table_sql, logging):
    try:
        cur = db_conn.cursor()
        cur.execute(create_table_sql)
        db_conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        logging.error(error)


def create_tables(db_conn, logging):
    create_table(db_conn, sql_crea_tabella_film, logging)
    create_table(db_conn, sql_crea_tabella_genere, logging)
    create_table(db_conn, sql_crea_tabella_spettacolo, logging)


sql_delete_all = " DELETE FROM %s "


def wipe_table(db_conn, table_name, logging):
    try:
        cur = db_conn.cursor()
        cur.execute("DELETE FROM " + table_name)
        db_conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        logging.error(error)


def wipe_tables(db_conn, logging):
    wipe_table(db_conn, "genere", logging)
    wipe_table(db_conn, "spettacolo", logging)
    wipe_table(db_conn, "film", logging)


sql_select_film = """   SELECT *
                        FROM film
                        WHERE id = %s """


sql_select_film_all = """   SELECT *
                            FROM film   """


def select_film(db_conn, id_film=None):
    cur = db_conn.cursor()
    if id_film is None:
        cur.execute(sql_select_film_all)
        films = []
        film_tuple = cur.fetchall()
        for film_tupla in film_tuple:
            films.append(Film(*film_tupla))
        return films
    cur.execute(sql_select_film, (id_film,))
    film_tupla = cur.fetchone()
    db_conn.commit()
    cur.close
    if film_tupla is None:
        return None
    return Film(*film_tupla)


sql_insert_film = """INSERT INTO film 
                     (id, titolo, data_uscita, regista, attori, trama, durata, trailer_link, locandina_link, locandina)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """


def insert_film(db_conn, film, generi):
    selected_film = select_film(db_conn, film.id_film)
    if selected_film is not None:
        return False
    cur = db_conn.cursor()
    cur.execute(sql_insert_film, (
        film.id_film, film.titolo, film.data_uscita, film.regista, film.attori, film.trama, film.durata,
        film.trailer_link, film.locandina_link, film.locandina))
    db_conn.commit()
    cur.close()
    for genere in generi:
        insert_genere(db_conn, genere)
    return True


sql_update_film_locandina = """ UPDATE film
                                SET locandina = %s
                                WHERE id = %s """


def update_film_locandina(db_conn, film, check_esistenza=False):
    if check_esistenza:
        selected_film = select_film(db_conn, film.id_film)
        if selected_film is not None:
            return False
    cur = db_conn.cursor()
    cur.execute(sql_update_film_locandina, (film.locandina, film.id_film))
    db_conn.commit()
    cur.close()
    return True


sql_insert_genere = """     INSERT INTO genere (id_film, genere)
                            VALUES (%s,%s) """


def insert_genere(db_conn, genere):
    cur = db_conn.cursor()
    cur.execute(sql_insert_genere, (genere.id_film, genere.genere))
    db_conn.commit()
    cur.close()
    return True


sql_select_generi = """ SELECT genere
                        FROM genere
                        WHERE id_film = %s """


def select_generi(db_conn, id_film):
    cur = db_conn.cursor()
    cur.execute(sql_select_generi, (id_film,))
    generi_tuple = cur.fetchall()
    db_conn.commit()
    cur.close()
    if generi_tuple is None:
        return None
    generi = []
    for genere in generi_tuple:
        generi.append(genere[0])
    return generi


sql_select_spettacolo = """ SELECT id, id_film, data_ora, sala, data, ora
                            FROM spettacolo
                            WHERE id = %s """


def select_spettacolo(db_conn, id_film):
    cur = db_conn.cursor()
    cur.execute(sql_select_spettacolo, (id_film,))
    spettacolo_tupla = cur.fetchone()
    db_conn.commit()
    cur.close()
    if spettacolo_tupla is None:
        return None
    return Spettacolo(*spettacolo_tupla)


sql_insert_spettacolo = """ INSERT INTO spettacolo (id, id_film, data_ora, sala, data, ora, consolidato)
                            VALUES (%s,%s,%s,%s,%s,%s,TRUE) """

sql_consolida_spettacolo = """  UPDATE spettacolo
                                SET consolidato = TRUE 
                                WHERE id = %s """


def insert_spettacolo(db_conn, spettacolo):
    selected_spettacolo = select_spettacolo(db_conn, spettacolo.id_spettacolo)
    cur = db_conn.cursor()
    if selected_spettacolo is not None:
        cur.execute(sql_consolida_spettacolo, (spettacolo.id_spettacolo,))
        db_conn.commit()
        return False
    adesso = datetime.now(timezone('Europe/Rome'))
    if adesso > string2datetime(spettacolo.data_ora):
        return False
    cur.execute(sql_insert_spettacolo, (spettacolo.id_spettacolo, spettacolo.id_film, spettacolo.data_ora,
                                        spettacolo.sala, spettacolo.data, spettacolo.ora))
    db_conn.commit()
    cur.close()
    return True


sql_select_spettacoli_all = """ SELECT id, id_film, data_ora, sala, data, ora
                            FROM spettacolo """

sql_select_spettacoli = """ SELECT id, id_film, data_ora, sala, data, ora
                            FROM spettacolo 
                            WHERE id_film = %s """


def select_spettacoli(db_conn, id_film=None):
    cur = db_conn.cursor()
    if id_film:
        cur.execute(sql_select_spettacoli, (id_film, ))
    else:
        cur.execute(sql_select_spettacoli_all)
    spettacoli_tupla = cur.fetchall()
    db_conn.commit()
    cur.close()
    if spettacoli_tupla is None:
        return []
    spettacoli = []
    for spettacolo_tupla in spettacoli_tupla:
        spettacoli.append(Spettacolo(*spettacolo_tupla))
    return spettacoli


sql_delete_spettacolo = """ DELETE FROM spettacolo 
                            WHERE id = %s"""


def elimina_spettacoli_passati(db_conn):
    adesso = datetime.now(timezone('Europe/Rome'))
    cur = db_conn.cursor()
    cur.execute(sql_select_spettacoli_all)
    spettacoli = cur.fetchall()
    if spettacoli is None:
        db_conn.commit()
        cur.close()
        return []

    spettacoli_rimossi = []
    for spettacolo_tupla in spettacoli:
        spettacolo = Spettacolo(*spettacolo_tupla)
        if string2datetime(spettacolo.data_ora) < adesso:
            cur.execute(sql_delete_spettacolo, (spettacolo.id_spettacolo,))
            db_conn.commit()
    cur.close()
    return spettacoli_rimossi


sql_delete_spettacoli_non_consolidati = """ DELETE FROM spettacolo 
                                            WHERE consolidato = FALSE """


def elimina_spettacoli_non_consolidati(db_conn):
    cur = db_conn.cursor()
    cur.execute(sql_delete_spettacoli_non_consolidati)
    db_conn.commit()
    cur.close()


sql_select_spettacoli_non_consolidati = """ SELECT id, id_film, data_ora, sala, data, ora
                                            FROM spettacolo 
                                            WHERE consolidato = FALSE """


def select_spettacoli_non_consolidati(db_conn):
    cur = db_conn.cursor()
    cur.execute(sql_select_spettacoli_non_consolidati)
    spettacoli_tupla = cur.fetchall()
    db_conn.commit()
    cur.close()
    if spettacoli_tupla is None:
        return []
    spettacoli = []
    for spettacolo_tupla in spettacoli_tupla:
        spettacoli.append(Spettacolo(*spettacolo_tupla))
    return spettacoli


sql_azzera_flag_spettacoli_consolidati = """ UPDATE spettacolo
                                             SET consolidato = FALSE """


def azzera_flag_spettacoli_consolidati(db_conn):
    cur = db_conn.cursor()
    cur.execute(sql_azzera_flag_spettacoli_consolidati)
    db_conn.commit()
    cur.close()