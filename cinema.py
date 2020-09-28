#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import logging
import os
import time
from sqlite3.dbapi2 import Connection

import emoji
import requests
import telepot
from telepot.loop import MessageLoop

import handleDB
from Film import Film
from Genere import Genere
from Spettacolo import Spettacolo, ordina_spettacoli_film_data, ordina_spettacoli_data, render_spettacoli_per_data

# token that can be generated talking with BotFather on telegram
my_token = os.environ.get('TOKEN_HEROKU')
my_id = os.environ.get('MY_ID_HEROKU')

aiuto = ["aiuto", "/aiuto", "help", "/help", "/start"]
programmazioneGiornaliera = ["/showperdata"]
programmazioneGiornalieraCompleta = ["/showperdataall", "/showperdatacomplete", "/showperdatatutti"]
programmazionePerFilm = ["/showperfilm"]
aggiornamento = ["/update", "/aggiornamenti", "/aggiornamento"]

msg_benvenuto = 'Ciao, sono il bot non ufficiale del The Space di Bologna. ' \
                'Ecco le cose che puoi chiedermi:' \
                '\n/aiuto per ricevere questo messaggio' \
                '\n/showPerData per ricevere la programmazione per data' \
                '\n/showPerFilm per ricevere la programmazione per film' \
                '\n/aggiornamenti per sapere cosa è cambiato nell\'ultimo aggiornamento della programmazione'


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        logging.info(msg)
        messaggio = msg.get("text").strip().lower()
        if messaggio in aiuto:
            bot.sendMessage(chat_id, msg_benvenuto)
        elif messaggio in programmazioneGiornaliera:
            bot.sendMessage(chat_id, "--PROGRAMMAZIONE PER DATA--\n\n"
                            + emoji.emojize(get_spettacoli_per_data(), use_aliases=True)
                            + "\n\nSono mostrati gli spettacoli dei prossimi 7 giorni, per vederli tutti digita /showPerDataAll.")
        else:
            logging.warning("Messaggio sconosciuto ricevuto - " + msg)
            bot.sendMessage(chat_id, emoji.emojize("Non ho capito... :sob:", use_aliases=True))


def get_spettacoli_per_data():
    db_conn = handleDB.create_db(r"cinema.db", logging)
    if db_conn is None:
        print("ERRORE - Impossibile creare connessione con il DB")
        raise Exception("ERRORE - Impossibile creare connessione con il DB")
    handleDB.create_tables(db_conn, logging)
    spettacoli = handleDB.select_spettacoli(db_conn)
    return render_spettacoli_per_data(db_conn, spettacoli)


def send_request():
    try:
        response = requests.get(
            url="https://www.thespacecinema.it/data/filmswithshowings/3",
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        return response.text
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


logging.basicConfig(filename='bot.log', format='[%(asctime)s]%(levelname)s:%(message)s', level=logging.DEBUG)
bot = telepot.Bot(my_token)
bot.sendMessage(my_id, msg_benvenuto)
MessageLoop(bot, handle).run_as_thread()

while True:
    try:
        db_conn = handleDB.create_db(r"cinema.db", logging)
        if db_conn is None:
            print("ERRORE - Impossibile creare connessione con il DB")
            raise Exception("ERRORE - Impossibile creare connessione con il DB")
        handleDB.create_tables(db_conn, logging)

        handleDB.elimina_spettacoli_passati(db_conn)
        handleDB.elimina_spettacoli_non_consolidati(db_conn)
        handleDB.azzera_flag_spettacoli_consolidati(db_conn)

        raw = send_request()
        jsonData = json.loads(raw)
        nuoviFilm = []
        nuoviSpettacoli = []
        for filmTS in jsonData["films"]:
            filmDB = Film(
                (filmTS.get("id"), filmTS.get("title"), filmTS.get("ReleaseDate"), filmTS.get("info_director"),
                 filmTS.get("info_cast"), filmTS.get("synopsis_short"), filmTS.get("info_runningtime"),
                 filmTS.get("video"), None))
            generi = []
            for genereTS in (filmTS.get("genres"))["names"]:
                generi.append(Genere((filmDB.id, genereTS.get("name"))))
            if handleDB.insert_film(db_conn, filmDB, generi):
                nuoviFilm.append(filmDB)
            for spettacoloTS in filmTS["showings"]:
                for orarioTS in spettacoloTS["times"]:
                    spettacoloDB = Spettacolo((orarioTS.get("session_id"), filmDB.id, orarioTS.get("date"),
                                               orarioTS.get("screen_number"), spettacoloTS.get("date_short"),
                                               orarioTS.get("time")))
                    if handleDB.insert_spettacolo(db_conn, spettacoloDB):
                        nuoviSpettacoli.append(spettacoloDB)
        spettacoliRimossi = handleDB.select_spettacoli_non_consolidati(db_conn)

        aggiornamento = ""
        if nuoviFilm:
            aggiornamento = aggiornamento + "\n:white_check_mark: FILM AGGIUNTI :white_check_mark:\n"
            for film in nuoviFilm:
                aggiornamento += film.titolo + "\n"
        if nuoviSpettacoli:
            ordina_spettacoli_film_data(nuoviSpettacoli)
            aggiornamento = aggiornamento + "\n:white_check_mark: SPETTACOLI AGGIUNTI :white_check_mark:\n"
            for spettacolo in nuoviSpettacoli:
                aggiornamento += handleDB.select_film(db_conn, spettacolo.id_film).titolo + " - " + spettacolo.data + " " \
                                    + spettacolo.ora + "\n"
        if spettacoliRimossi:
            ordina_spettacoli_film_data(spettacoliRimossi)
            aggiornamento = aggiornamento + "\n:no_entry: SPETTACOLI RIMOSSI :no_entry:\n"
            for spettacolo in spettacoliRimossi:
                aggiornamento += handleDB.select_film(db_conn, spettacolo.id_film).titolo + " - " + spettacolo.data + " " \
                                 + spettacolo.ora + "\n"
        if aggiornamento is not "":
            bot.sendMessage(my_id, emoji.emojize(aggiornamento, use_aliases=True))

        db_conn.close()

    except Exception as e:
        print("ERRORE\n"+ e.message)
        logging.error(e)
        bot.sendMessage(my_id, "\nErrore nel recupero o nell'elaborazione delle informazioni")
        if db_conn is not None:
            db_conn.close()

    time.sleep(300)
